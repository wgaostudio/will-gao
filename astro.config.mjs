import { defineConfig } from 'astro/config';
export default defineConfig({ site: process.env.SITE_URL || 'https://will-gao-notebook.wgaostudio.chatgpt.site', base: process.env.BASE_PATH || '/', output: 'static', trailingSlash: 'always' });
