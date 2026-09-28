// @ts-check
import { defineConfig } from 'astro/config';

import mdx from '@astrojs/mdx';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://jiang-li.github.io',
  // 'preserve' keeps index.mdx -> dir/index.html (like Quarto) while
  // other pages become page.html — matching the original URL structure
  build: {
    format: 'preserve',
  },
  integrations: [mdx()],

  vite: {
    plugins: [tailwindcss()],
  },
});
