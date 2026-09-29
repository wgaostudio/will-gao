"""Convert the repository's simple expository LaTeX notes to site HTML.

This intentionally supports the small, semantic LaTeX subset used by Will's
notes: sections, theorem-style environments, proofs, enumerations, paragraph
heads, and inline/display mathematics. MathJax performs the final math render.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


STATEMENTS = {
    "theorem": "Theorem",
    "proposition": "Proposition",
    "lemma": "Lemma",
    "corollary": "Corollary",
    "definition": "Definition",
    "example": "Example",
    "remark": "Remark",
}


def balanced_command(text: str, command: str) -> tuple[str, str] | None:
    prefix = f"\\{command}{{"
    if not text.startswith(prefix):
        return None
    depth = 1
    index = len(prefix)
    while index < len(text) and depth:
        if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
        index += 1
    if depth:
        raise ValueError(f"Unclosed \\{command} command")
    return text[len(prefix) : index - 1], text[index:]


class Converter:
    def __init__(self, source: str):
        self.source = source
        self.section = 0
        self.statement = 0
        self.equation = 0
        self.labels: dict[str, tuple[str, str]] = {}
        self.toc: list[dict[str, str | int]] = []

    def convert(self) -> tuple[str, list[dict[str, str | int]]]:
        body = re.search(r"\\begin\{document\}(.*)\\end\{document\}", self.source, re.S)
        if not body:
            raise ValueError("No LaTeX document body found")
        text = body.group(1)
        text = re.sub(r"\\maketitle\s*", "", text)
        rendered = self.blocks(text)
        rendered = self.resolve_references(rendered)
        intro, first_section, remainder = rendered.partition("<h2")
        if first_section:
            disclaimer = "I have done my best to ensure correctness, but errors may remain."
            if disclaimer not in intro:
                intro = intro.rstrip() + f"\n<p>{disclaimer}</p>\n"
            rendered = (
                '<div class="frontmatter notice">\n'
                f"{intro.strip()}\n"
                "</div>\n"
                f"<h2{remainder}"
            )
        return f'<div class="latex-note">\n{rendered}\n</div>\n', self.toc

    def blocks(self, text: str) -> str:
        lines = text.strip().splitlines()
        output: list[str] = []
        paragraph: list[str] = []
        paragraph_head_title: str | None = None
        index = 0

        def flush() -> None:
            nonlocal paragraph_head_title
            if not paragraph:
                return
            prose = " ".join(part.strip() for part in paragraph if part.strip())
            paragraph.clear()
            if prose:
                prefix = (
                    f"<strong>{self.inline(paragraph_head_title)}</strong> "
                    if paragraph_head_title
                    else ""
                )
                output.append(f"<p>{prefix}{self.inline(prose)}</p>")
            paragraph_head_title = None

        while index < len(lines):
            stripped = lines[index].strip()
            if not stripped:
                flush()
                index += 1
                continue

            section = re.fullmatch(r"\\section\{(.+)\}", stripped)
            if section:
                flush()
                self.section += 1
                self.statement = 0
                title = section.group(1)
                ident = f"section-{self.section}"
                self.toc.append({"id": ident, "title": f"{self.section} {title}", "level": 2})
                output.append(
                    f'<h2 id="{ident}"><span class="secnum">{self.section}</span>'
                    f"{self.inline(title)}</h2>"
                )
                index += 1
                continue

            paragraph_head = re.match(r"\\paragraph\{(.+?)\}(.*)", stripped)
            if paragraph_head:
                flush()
                title, remainder = paragraph_head.groups()
                paragraph_head_title = title
                if remainder.strip():
                    paragraph.append(remainder.strip())
                index += 1
                continue

            begin = re.match(r"\\begin\{([^}]+)\}(?:\[([^]]+)\])?(.*)", stripped)
            if begin:
                environment, optional, remainder = begin.groups()
                if environment in set(STATEMENTS) | {"proof", "enumerate", "equation", "align*"}:
                    flush()
                    content_lines = [remainder] if remainder.strip() else []
                    depth = 1
                    index += 1
                    while index < len(lines):
                        candidate = lines[index]
                        depth += len(re.findall(rf"\\begin\{{{re.escape(environment)}\}}", candidate))
                        if re.search(rf"\\end\{{{re.escape(environment)}\}}", candidate):
                            depth -= 1
                            if depth == 0:
                                before = re.split(rf"\\end\{{{re.escape(environment)}\}}", candidate, 1)[0]
                                if before.strip():
                                    content_lines.append(before)
                                break
                        content_lines.append(candidate)
                        index += 1
                    if depth:
                        raise ValueError(f"Unclosed {environment} environment")
                    content = "\n".join(content_lines).strip()
                    output.append(self.environment(environment, optional, content))
                    index += 1
                    continue

            if stripped == r"\[" or stripped.startswith(r"\["):
                flush()
                math_lines: list[str] = []
                first = stripped[2:]
                if first:
                    math_lines.append(first)
                index += 1
                while index < len(lines):
                    candidate = lines[index]
                    if r"\]" in candidate:
                        math_lines.append(candidate.split(r"\]", 1)[0])
                        break
                    math_lines.append(candidate)
                    index += 1
                output.append(self.display_math("\n".join(math_lines).strip()))
                index += 1
                continue

            paragraph.append(stripped)
            index += 1

        flush()
        return "\n".join(output)

    def environment(self, name: str, optional: str | None, content: str) -> str:
        if name in STATEMENTS:
            self.statement += 1
            number = f"{self.section}.{self.statement}"
            label = self.extract_label(content)
            if label:
                self.labels[label] = (number, f"{name}-{number.replace('.', '-')}")
                content = re.sub(rf"\\label\{{{re.escape(label)}\}}", "", content, count=1)
            ident = self.labels.get(label, ("", f"{name}-{number.replace('.', '-')}"))[1]
            title = STATEMENTS[name] + f" {number}"
            if optional:
                title += f" ({self.inline(optional)})"
            return (
                f'<div class="{name} statement" id="{ident}">\n'
                f'  <span class="head">{title}.</span>\n'
                f'  <div class="body">{self.blocks(content)}</div>\n'
                "</div>"
            )
        if name == "proof":
            return (
                '<div class="proof proof-block">\n'
                '  <span class="head">Proof.</span>\n'
                f"  {self.blocks(content)}\n"
                '  <span class="qed" aria-label="End of proof">□</span>\n'
                "</div>"
            )
        if name == "enumerate":
            items = re.split(r"(?m)^\s*\\item\s*", content)
            rendered = [f"<li>{self.blocks(item)}</li>" for item in items if item.strip()]
            return "<ol>\n" + "\n".join(rendered) + "\n</ol>"
        if name == "equation":
            self.equation += 1
            label = self.extract_label(content)
            if label:
                ident = f"equation-{self.equation}"
                self.labels[label] = (str(self.equation), ident)
                content = re.sub(rf"\\label\{{{re.escape(label)}\}}", "", content, count=1)
            else:
                ident = f"equation-{self.equation}"
            return self.display_math(content, str(self.equation), ident)
        if name == "align*":
            return self.display_math(r"\begin{aligned}" + content + r"\end{aligned}")
        raise ValueError(f"Unsupported environment: {name}")

    @staticmethod
    def extract_label(content: str) -> str | None:
        match = re.search(r"\\label\{([^}]+)\}", content)
        return match.group(1) if match else None

    @staticmethod
    def display_math(math: str, number: str | None = None, ident: str | None = None) -> str:
        id_attr = f' id="{ident}"' if ident else ""
        number_html = f'<span class="eqno">({number})</span>' if number else ""
        return (
            f'<div class="eq"{id_attr}><div class="mathwrap">\\[{math}\\]</div>'
            f"{number_html}</div>"
        )

    def inline(self, text: str) -> str:
        placeholders: list[str] = []

        def hold(value: str) -> str:
            token = f"@@HELD{len(placeholders)}@@"
            placeholders.append(value)
            return token

        for command, tag in (("emph", "em"), ("textit", "em")):
            while f"\\{command}{{" in text:
                start = text.index(f"\\{command}{{")
                parsed = balanced_command(text[start:], command)
                if not parsed:
                    break
                inside, rest = parsed
                consumed = len(text[start:]) - len(rest)
                replacement = hold(f"<{tag}>{self.inline(inside)}</{tag}>")
                text = text[:start] + replacement + text[start + consumed :]

        def math_hold(match: re.Match[str]) -> str:
            return hold(r"\(" + match.group(1) + r"\)")

        text = re.sub(r"(?<!\\)\$(.+?)(?<!\\)\$", math_hold, text)

        text = re.sub(
            r"\\eqref\{([^}]+)\}",
            lambda match: hold(f"@@EQREF:{match.group(1)}@@"),
            text,
        )
        text = re.sub(
            r"\\ref\{([^}]+)\}",
            lambda match: hold(f"@@REF:{match.group(1)}@@"),
            text,
        )
        text = html.escape(text, quote=False)
        text = text.replace("``", "“").replace("''", "”")
        text = text.replace("---", "—").replace("--", "–")
        text = text.replace(r"\%", "%").replace(r"\&", "&amp;")
        text = text.replace(r"\. ", ". ").replace(r"\ ", " ")
        text = text.replace("~", "&nbsp;")
        for index, value in enumerate(placeholders):
            text = text.replace(f"@@HELD{index}@@", value)
        return text

    def resolve_references(self, rendered: str) -> str:
        def ref(match: re.Match[str]) -> str:
            kind, label = match.groups()
            if label not in self.labels:
                raise ValueError(f"Unknown reference: {label}")
            number, ident = self.labels[label]
            visible = f"({number})" if kind == "EQREF" else number
            return f'<a href="#{ident}">{visible}</a>'

        return re.sub(r"@@(EQREF|REF):([^@]+)@@", ref, rendered)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("slug")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    converter = Converter(args.source.read_text())
    content, toc = converter.convert()
    (root / "src/content" / f"{args.slug}.html").write_text(content)
    (root / "src/data" / f"{args.slug}-toc.json").write_text(
        json.dumps(toc, indent=2, ensure_ascii=False) + "\n"
    )


if __name__ == "__main__":
    main()
