# FoodDB Compound Explorer

A scientific analytical backend and comparison workbench over curated FoodDB-derived artifacts. It combines DuckDB/Parquet evidence queries with vectorized NumPy descriptor representations to support bidirectional food-compound exploration, chemical-profile comparison, and interpretable similarity retrieval.

## Engineering profile

This repository demonstrates:

- DuckDB analytical SQL with CTEs, joins, filters, and parameterized queries
- Food-to-compound and compound-to-food evidence navigation
- Links to flavor terms, enzymes, pathways, and health-effect evidence
- Raw, standardized, and IDF-weighted descriptor vectors
- Vectorized NumPy cosine similarity and full-matrix nearest-profile ranking
- Interpretable descriptor deltas instead of opaque similarity-only output
- Hugging Face artifact hydration decoupled from upstream data-build environment

## Reliability and scope

This serving repository consumes curated descriptor/data artifacts.

## Related artifacts

- **Hugging Face artifacts/data:** https://huggingface.co/datasets/noirchoix/fooddb

## Data Source

Hugging Face dataset:

```text
noirchoix/fooddb
```

Expected artifact layout:

```text
food_chemistry/staging/fooddb.duckdb
food_chemistry/curated/v1/*.parquet
food_chemistry/curated/v1/*.json
```

At runtime these are cached locally under:

```text
apps/api/data/
```

That directory is intentionally ignored by Git.

## Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/api/v1/fooddb/health
```

## Frontend

```bash
cd apps/web
npm install
cp .env.example .env
npm run dev -- --host 0.0.0.0
```

Open:

```text
http://localhost:5173
```

## Docker Compose

```bash
docker compose up
```

This starts:

```text
FastAPI API: http://localhost:8000
SvelteKit UI: http://localhost:5173
```

## Environment

Backend:

```env
FOODDB_HF_REPO_ID=noirchoix/fooddb
FOODDB_HF_REPO_TYPE=dataset
FOODDB_AUTO_DOWNLOAD=true
FOODDB_CACHE_DIR=./apps/api/data
FOODDB_DUCKDB_PATH=./apps/api/data/food_chemistry/staging/fooddb.duckdb
FOODDB_CURATED_DIR=./apps/api/data/food_chemistry/curated/v1
FOODDB_DEFAULT_VECTOR_POLICY=zscore
FOODDB_MAX_LIMIT=500
FOODDB_QUERY_TIMEOUT_SECONDS=30
FRONTEND_ORIGIN=http://localhost:5173
```

Frontend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## API

```text
GET /api/v1/fooddb/health
GET /api/v1/fooddb/foods/search?q=angel&limit=20
GET /api/v1/fooddb/foods/resolve?q=Angelica
GET /api/v1/fooddb/foods/{food_id}
GET /api/v1/fooddb/foods/{food_id}/compounds
GET /api/v1/fooddb/compounds/search?q=quercetin&limit=20
GET /api/v1/fooddb/compounds/{compound_id}
GET /api/v1/fooddb/compounds/{compound_id}/foods
GET /api/v1/fooddb/compounds/{compound_id}/bio-links
GET /api/v1/fooddb/foods/{food_id}/vector?policy=zscore
GET /api/v1/fooddb/foods/compare?food_a=Angelica&food_b=Ginger&policy=zscore
GET /api/v1/fooddb/foods/similar?q=Angelica&policy=zscore&top_k=10
```

## Deployment Notes

Recommended setup:

- Backend on Render or Railway.
- Frontend on Netlify or Vercel.
- Dataset artifacts on Hugging Face at `noirchoix/fooddb`.

On the backend host, set the environment variables from `apps/api/.env.example`. The first backend startup downloads the FoodDB artifacts into the instance filesystem. If the platform has an ephemeral filesystem, expect a cold-start download after redeploys.

For persistent storage, mount a disk at:

```text
apps/api/data
```

## Smoke Test

After backend dependencies are installed:

```bash
cd apps/api
python scripts/smoke_fooddb.py
```

## Implementation Notes

- DuckDB is the canonical store for food, compound, and concentration browsing.
- Curated Parquet artifacts power descriptor vectors, similarity, and bio-link metadata.
- No vector database is required.
- No LLM inference is required for this app.
- The repo intentionally excludes the FoodDB binary artifacts; Hugging Face is the source of truth.
