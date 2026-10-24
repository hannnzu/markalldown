# Frontend — Next.js

Belum di-scaffold; ikuti `../docs/IMPLEMENTATION_PLAN.md` Phase 6 (`create-next-app ... --src-dir`, lalu kunci versi di `../CHANGELOG.md`).

```bash
cp .env.local.example .env.local
npm run dev
npx vitest run     # baseline: 15 failed (tests/spec-001.test.ts)
```

Aturan penting: pratinjau memakai `react-markdown` + `remark-gfm` tanpa `rehype-raw` (NFR-S7); antarmuka berbahasa Indonesia.
