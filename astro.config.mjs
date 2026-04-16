import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://yichen-gao.github.io',
  output: 'static',
  integrations: [sitemap()],
  vite: {
    server: {
      host: true,
    },
  },
});
