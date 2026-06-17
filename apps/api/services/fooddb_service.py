from __future__ import annotations

from core.config import Settings
from core.errors import FoodDBError
from repositories.fooddb_repository import FoodDBRepository
from services.hf_assets import ensure_fooddb_assets


class FoodDBService:
    def __init__(self, settings: Settings) -> None:
        ensure_fooddb_assets(settings)
        self.repository = FoodDBRepository(
            duckdb_path=settings.resolved_duckdb_path(),
            curated_dir=settings.resolved_curated_dir(),
            max_limit=settings.fooddb_max_limit,
        )

    def health(self):
        return self.repository.health()

    def search_foods(self, q: str, limit: int):
        self._validate_query(q)
        return self.repository.search_foods(q, limit)

    def resolve_food(self, q: str):
        self._validate_query(q)
        return self.repository.resolve_food(q)

    def get_food(self, food_id: int):
        return self.repository.get_food(food_id)

    def food_compounds(self, food_id: int, limit: int, measured_only: bool):
        return self.repository.food_compounds(food_id, limit, measured_only)

    def search_compounds(self, q: str, limit: int):
        self._validate_query(q)
        return self.repository.search_compounds(q, limit)

    def get_compound(self, compound_id: int):
        return self.repository.get_compound(compound_id)

    def compound_foods(self, compound_id: int, limit: int, measured_only: bool):
        return self.repository.compound_foods(compound_id, limit, measured_only)

    def bio_links(self, compound_id: int, limit_per_kind: int):
        return self.repository.bio_links(compound_id, limit_per_kind)

    def vector_for_food(self, food_id: int, policy: str):
        return self.repository.vector_for_food(food_id, policy)

    def compare_foods(self, food_a: str, food_b: str, policy: str):
        self._validate_query(food_a)
        self._validate_query(food_b)
        a = self.repository.resolve_food(food_a)
        b = self.repository.resolve_food(food_b)
        if not a or not b:
            return None
        comparison = self.repository.compare_foods(a['food_id'], b['food_id'], policy)
        if comparison is None:
            return None
        similarity, metric_deltas = comparison
        return {'food_a': a, 'food_b': b, 'policy': policy, 'similarity': similarity, 'metric_deltas': metric_deltas}

    def similar_foods(self, q: str, policy: str, top_k: int):
        self._validate_query(q)
        food = self.repository.resolve_food(q)
        if not food:
            return None
        return self.repository.similar_foods(food['food_id'], policy, top_k)

    @staticmethod
    def _validate_query(q: str) -> None:
        if not q or not q.strip():
            raise FoodDBError('Query cannot be empty.', code='empty_query')
