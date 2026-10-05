// @ts-check
import { existsSync } from 'node:fs';

import { defineConfig } from 'astro/config';

import mdx from '@astrojs/mdx';
import tailwindcss from '@tailwindcss/vite';

import sitemap from '@astrojs/sitemap';

import { satteri } from '@astrojs/markdown-satteri';

import tableScrollPlugin from './src/plugins/rehype-table-scroll.mjs';

// https://astro.build/config
export default defineConfig({
  site: 'https://jiang-li.github.io',
  // 'preserve' keeps index.mdx -> dir/index.html (like Quarto) while
  // other pages become page.html — matching the original URL structure
  build: {
    format: 'preserve',
  },
  // Astro's Shiki default is `github-dark`; the Quarto site it replaced
  // rendered code blocks light, and the owner chose to keep that.
  markdown: {
    shikiConfig: {
      theme: 'github-light',
    },
    // Content tables are wider than a phone. `table-scroll` drops each one into
    // the same `.table-scroll` container careers.astro writes by hand, so the
    // table scrolls inside itself instead of pushing the page sideways.
    // Astro 7's default Markdown processor is Sätteri, so this is a hast plugin
    // on `satteri()` rather than a `rehypePlugins` entry. @astrojs/mdx inherits
    // `markdown.processor` by default, so the four MDX guides get it too.
    processor: satteri({ hastPlugins: [tableScrollPlugin()] }),
  },
  integrations: [
    mdx(),
    sitemap({
      // @astrojs/sitemap emits extension-less URLs, but build.format 'preserve'
      // writes course.html / teach/<slug>/index.html. Rewrite each entry to the
      // file that actually ships, matching the URL shape of the old Quarto sitemap.
      serialize(item) {
        const url = new URL(item.url);
        const slug = url.pathname.replace(/^\/|\/$/g, '');
        if (slug === '') {
          url.pathname = '/index.html';
        } else if (!url.pathname.endsWith('.html')) {
          // A page authored as src/pages/<slug>/index.mdx ships at <slug>/index.html;
          // everything else ships at <slug>.html.
          const isDirPage = ['.mdx', '.md', '.astro'].some((ext) =>
            existsSync(new URL(`./src/pages/${slug}/index${ext}`, import.meta.url)),
          );
          url.pathname = isDirPage ? `/${slug}/index.html` : `/${slug}.html`;
        }
        return { ...item, url: url.href };
      },
    }),
  ],

  vite: {
    plugins: [tailwindcss()],
  },
});