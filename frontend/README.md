# Image Analysis Agent — Frontend

Web dashboard for the Image Analysis Agent: upload images (single or bulk), view analysis results and tag records, search by filters, and browse recently tagged images.

---

## Tech stack

- **Next.js 16** (App Router)
- **React 19** · **TypeScript**
- **Tailwind CSS v4** · **shadcn/ui**
- **Framer Motion** · **Lucide React** · **react-dropzone** · **Sonner** (toasts)

---

## Prerequisites

- **Node.js 20+**
- Backend API running (e.g. `http://localhost:8000`) for full functionality

---

## Getting started

```bash
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). For production build and run:

```bash
npm run build
npm start
```

---

## Scripts

| Command | Description |
|--------|-------------|
| `npm run dev` | Start dev server with hot reload. |
| `npm run build` | Production build (Next.js). |
| `npm start` | Serve production build. |
| `npm run lint` | Run ESLint. |

---

## Project structure

```
frontend/src/
├── app/                 # App Router pages and layout
│   ├── page.tsx         # Home: upload, result, history, bulk
│   ├── search/          # Search page (filters + results)
│   ├── layout.tsx
│   ├── error.tsx        # Error boundary
│   └── globals.css
├── components/          # UI components
│   ├── ImageUploader   # Single-file upload
│   ├── BulkUploader    # Multi-file upload + progress
│   ├── DashboardResult # Analysis result (tags, flagged, JSON)
│   ├── FilterSidebar   # Search filters (taxonomy chips)
│   ├── SearchResults   # Search grid + detail modal
│   ├── HistoryGrid     # Recently tagged images
│   └── ui/             # shadcn components
└── lib/                # Types, constants, utilities
    ├── types.ts
    ├── constants.ts
    ├── formatTag.ts
    └── utils.ts
```

---

## API usage

The frontend calls the backend at `NEXT_PUBLIC_API_URL`:

- `POST /api/analyze-image` — single image analysis
- `POST /api/bulk-upload` · `GET /api/bulk-status/{batch_id}` — bulk processing
- `GET /api/tag-images` · `GET /api/tag-image/{id}` — history and detail
- `GET /api/search-images` · `GET /api/available-filters` — search and cascading filters
- `GET /api/taxonomy` — tag categories and values for filter UI

See the [API reference](../docs/architecture/API.md) and the [root README](../README.md) for the full stack.
