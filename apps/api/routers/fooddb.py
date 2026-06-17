from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from core.config import Settings, get_settings
from core.errors import FoodDBError, bad_request, not_found
from schemas.fooddb import (
    BioLink,
    CompoundDetail,
    CompoundFoodEdge,
    CompoundSummary,
    FoodComparisonResponse,
    FoodCompoundEdge,
    FoodDetail,
    FoodSummary,
    HealthResponse,
    SimilarFood,
    VectorPolicy,
    VectorResponse,
)
from services.fooddb_service import FoodDBService

router = APIRouter(prefix='/fooddb', tags=['FoodDB Compound Explorer'])


@lru_cache
def _service() -> FoodDBService:
    return FoodDBService(get_settings())


def get_service(settings: Annotated[Settings, Depends(get_settings)]) -> FoodDBService:
    # Settings dependency keeps the route testable; cached service prevents repeated vector warmup.
    return _service()


@router.get('/health', response_model=HealthResponse)
def health(service: Annotated[FoodDBService, Depends(get_service)]):
    return service.health()


@router.get('/foods/search', response_model=list[FoodSummary])
def search_foods(
    q: Annotated[str, Query(min_length=1, max_length=120)],
    service: Annotated[FoodDBService, Depends(get_service)],
    limit: Annotated[int, Query(ge=1, le=500)] = 20,
):
    try:
        return service.search_foods(q, limit)
    except FoodDBError as exc:
        raise bad_request(exc.message)


@router.get('/foods/resolve', response_model=FoodSummary)
def resolve_food(
    q: Annotated[str, Query(min_length=1, max_length=120)],
    service: Annotated[FoodDBService, Depends(get_service)],
):
    try:
        food = service.resolve_food(q)
    except FoodDBError as exc:
        raise bad_request(exc.message)
    if not food:
        raise not_found(f'No food matched query: {q}')
    return food


@router.get('/foods/compare', response_model=FoodComparisonResponse)
def compare_foods(
    food_a: Annotated[str, Query(min_length=1, max_length=120)],
    food_b: Annotated[str, Query(min_length=1, max_length=120)],
    service: Annotated[FoodDBService, Depends(get_service)],
    policy: VectorPolicy = 'zscore',
):
    result = service.compare_foods(food_a, food_b, policy)
    if not result:
        raise not_found('One or both foods could not be resolved, or vector artifacts are unavailable.')
    return result


@router.get('/foods/similar', response_model=list[SimilarFood])
def similar_foods(
    q: Annotated[str, Query(min_length=1, max_length=120)],
    service: Annotated[FoodDBService, Depends(get_service)],
    policy: VectorPolicy = 'zscore',
    top_k: Annotated[int, Query(ge=1, le=100)] = 10,
):
    result = service.similar_foods(q, policy, top_k)
    if result is None:
        raise not_found(f'No food matched query: {q}')
    return result


@router.get('/foods/{food_id}', response_model=FoodDetail)
def get_food(food_id: int, service: Annotated[FoodDBService, Depends(get_service)]):
    food = service.get_food(food_id)
    if not food:
        raise not_found(f'Food not found: {food_id}')
    return food


@router.get('/foods/{food_id}/compounds', response_model=list[FoodCompoundEdge])
def food_compounds(
    food_id: int,
    service: Annotated[FoodDBService, Depends(get_service)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    measured_only: bool = False,
):
    return service.food_compounds(food_id, limit, measured_only)


@router.get('/foods/{food_id}/vector', response_model=VectorResponse)
def food_vector(
    food_id: int,
    service: Annotated[FoodDBService, Depends(get_service)],
    policy: VectorPolicy = 'zscore',
):
    result = service.vector_for_food(food_id, policy)
    if not result:
        raise not_found(f'No {policy} vector found for food: {food_id}')
    return result


@router.get('/compounds/search', response_model=list[CompoundSummary])
def search_compounds(
    q: Annotated[str, Query(min_length=1, max_length=120)],
    service: Annotated[FoodDBService, Depends(get_service)],
    limit: Annotated[int, Query(ge=1, le=500)] = 20,
):
    try:
        return service.search_compounds(q, limit)
    except FoodDBError as exc:
        raise bad_request(exc.message)


@router.get('/compounds/{compound_id}', response_model=CompoundDetail)
def get_compound(compound_id: int, service: Annotated[FoodDBService, Depends(get_service)]):
    compound = service.get_compound(compound_id)
    if not compound:
        raise not_found(f'Compound not found: {compound_id}')
    return compound


@router.get('/compounds/{compound_id}/foods', response_model=list[CompoundFoodEdge])
def compound_foods(
    compound_id: int,
    service: Annotated[FoodDBService, Depends(get_service)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    measured_only: bool = False,
):
    return service.compound_foods(compound_id, limit, measured_only)


@router.get('/compounds/{compound_id}/bio-links', response_model=list[BioLink])
def compound_bio_links(
    compound_id: int,
    service: Annotated[FoodDBService, Depends(get_service)],
    limit_per_kind: Annotated[int, Query(ge=1, le=100)] = 50,
):
    return service.bio_links(compound_id, limit_per_kind)
