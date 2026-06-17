from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.logging import configure_logging
from routers.fooddb import router as fooddb_router
from services.hf_assets import ensure_fooddb_assets

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, 'http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_credentials=True,
    allow_methods=['GET'],
    allow_headers=['*'],
)


@app.get('/health')
def root_health():
    return {'ok': True, 'app': settings.app_name}


@app.on_event('startup')
def hydrate_fooddb_assets():
    ensure_fooddb_assets(settings)


app.include_router(fooddb_router, prefix=settings.api_prefix)
