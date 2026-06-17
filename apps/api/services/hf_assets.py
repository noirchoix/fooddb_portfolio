from __future__ import annotations

import logging
from pathlib import Path

from huggingface_hub import hf_hub_download

from core.config import Settings

logger = logging.getLogger(__name__)

FOODDB_REQUIRED_FILES = [
    'food_chemistry/staging/fooddb.duckdb',
    'food_chemistry/curated/v1/compound_descriptor_failures.parquet',
    'food_chemistry/curated/v1/compound_descriptors.parquet',
    'food_chemistry/curated/v1/compound_enzyme_edges.parquet',
    'food_chemistry/curated/v1/compound_flavor_edges.parquet',
    'food_chemistry/curated/v1/compound_health_effect_edges.parquet',
    'food_chemistry/curated/v1/compound_idf.parquet',
    'food_chemistry/curated/v1/compound_pathway_edges.parquet',
    'food_chemistry/curated/v1/feature_manifest.json',
    'food_chemistry/curated/v1/food_compound_edges.parquet',
    'food_chemistry/curated/v1/food_descriptor_top_compounds.parquet',
    'food_chemistry/curated/v1/food_descriptor_vectors.parquet',
    'food_chemistry/curated/v1/food_descriptor_vectors_idf.parquet',
    'food_chemistry/curated/v1/food_descriptor_vectors_zscore.parquet',
    'food_chemistry/curated/v1/phase4_qc_report.json',
    'food_chemistry/curated/v1/vector_stats.json',
]


def ensure_fooddb_assets(settings: Settings) -> None:
    duckdb_path = settings.resolved_duckdb_path()
    curated_dir = settings.resolved_curated_dir()

    if duckdb_path.exists() and curated_dir.exists():
        missing_curated = [
            rel
            for rel in FOODDB_REQUIRED_FILES
            if rel.startswith('food_chemistry/curated/')
            and not (settings.resolved_cache_dir() / rel).exists()
        ]
        if not missing_curated:
            return

    if not settings.fooddb_auto_download:
        return

    cache_dir = settings.resolved_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    for repo_file in FOODDB_REQUIRED_FILES:
        target = cache_dir / repo_file
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        logger.info('Downloading FoodDB artifact from Hugging Face: %s', repo_file)
        downloaded = hf_hub_download(
            repo_id=settings.fooddb_hf_repo_id,
            repo_type=settings.fooddb_hf_repo_type,
            filename=repo_file,
            local_dir=cache_dir,
            local_dir_use_symlinks=False,
        )
        if not Path(downloaded).exists():
            raise FileNotFoundError(f'Hugging Face download did not produce expected file: {repo_file}')
