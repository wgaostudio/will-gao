import { defineConfig } from 'astro/config';
export default defineConfig({ site: 'https://willhgao.com', base: process.env.BASE_PATH || '/', output: 'static', trailingSlash: 'always' });
