# Yichen Gao personal site

A job-search ready personal site built with Astro and deployed to GitHub Pages.

## Local development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

## Content map

- `src/data/site.ts`: headline, contact links, homepage positioning
- `src/data/projects.ts`: featured project cards
- `src/data/resume.ts`: resume view content blocks
- `src/content/blog/`: markdown blog posts
- `src/styles/global.css`: site-wide visual system

## Before publishing widely

- Replace the placeholder email in `src/data/site.ts`
- Swap the weakest project placeholder for a real case study
- Tighten the headline so it matches the jobs you are applying for
- If you are creating a GitHub Pages user site, use the repo name `yichen-gao.github.io`
