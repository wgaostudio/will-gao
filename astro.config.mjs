import { defineConfig } from 'astro/config';
export default defineConfig({ site: process.env.SITE_URL || 'https://will-gao-notebook.wgaostudio.chatgpt.site', output: 'static', trailingSlash: 'always' });
