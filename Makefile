.PHONY: api web smoke zip

api:
	cd apps/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

web:
	cd apps/web && npm run dev -- --host 0.0.0.0

smoke:
	cd apps/api && python scripts/smoke_fooddb.py

zip:
	cd .. && zip -r fooddb_compound_explorer.zip fooddb_compound_explorer -x '*/node_modules/*' '*/.svelte-kit/*' '*/__pycache__/*'
