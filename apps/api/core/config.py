from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'FoodDB Compound Explorer API'
    api_prefix: str = '/api/v1'
    frontend_origin: str = 'http://localhost:5173'
    fooddb_hf_repo_id: str = 'noirchoix/fooddb'
    fooddb_hf_repo_type: str = 'dataset'
    fooddb_auto_download: bool = True
    fooddb_cache_dir: Path = Field(default=Path('./apps/api/data'))
    fooddb_duckdb_path: Path = Field(default=Path('./apps/api/data/food_chemistry/staging/fooddb.duckdb'))
    fooddb_curated_dir: Path = Field(default=Path('./apps/api/data/food_chemistry/curated/v1'))
    fooddb_default_vector_policy: str = 'zscore'
    fooddb_max_limit: int = 500
    fooddb_query_timeout_seconds: int = 30

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    def _resolve_project_path(self, path: Path) -> Path:
        if path.is_absolute() and path.exists():
            return path
        candidates = [
            Path.cwd() / path,
            Path(__file__).resolve().parents[1] / path,
            self.project_root / path,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return (self.project_root / path).resolve()

    def resolved_duckdb_path(self) -> Path:
        return self._resolve_project_path(self.fooddb_duckdb_path)

    def resolved_curated_dir(self) -> Path:
        return self._resolve_project_path(self.fooddb_curated_dir)

    def resolved_cache_dir(self) -> Path:
        return self._resolve_project_path(self.fooddb_cache_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
