from typing import Any, Literal
from pydantic import BaseModel, Field


VectorPolicy = Literal['raw', 'zscore', 'idf']


class HealthResponse(BaseModel):
    ok: bool
    database_path: str
    curated_dir: str
    foods: int
    compounds: int
    curated_edges: int
    vector_rows: int
    available_policies: list[str]
    qc_ok: bool | None = None


class FoodSummary(BaseModel):
    food_id: int
    public_id: str | None = None
    name: str
    name_scientific: str | None = None
    food_group: str | None = None
    food_subgroup: str | None = None
    food_type: str | None = None
    category: str | None = None
    ncbi_taxonomy_id: int | None = None


class FoodDetail(FoodSummary):
    description: str | None = None
    wikipedia_id: str | None = None


class CompoundSummary(BaseModel):
    compound_id: int
    public_id: str | None = None
    name: str
    cas_number: str | None = None
    inchikey: str | None = None
    inchi: str | None = None
    smiles: str | None = None
    moldb_mono_mass: float | None = None
    kingdom: str | None = None
    superklass: str | None = None
    klass: str | None = None
    subklass: str | None = None


class CompoundDetail(CompoundSummary):
    description: str | None = None
    annotation_quality: str | None = None


class FoodCompoundEdge(BaseModel):
    food_id: int
    compound_id: int
    compound_name: str | None = None
    inchikey: str | None = None
    presence: int | None = None
    standard_content: float | None = None
    orig_content: float | None = None
    orig_unit: str | None = None
    orig_min: float | None = None
    orig_max: float | None = None
    preparation_type: str | None = None
    citation: str | None = None
    citation_type: str | None = None


class CompoundFoodEdge(BaseModel):
    food_id: int
    food_name: str
    food_group: str | None = None
    food_subgroup: str | None = None
    compound_id: int
    standard_content: float | None = None
    orig_content: float | None = None
    orig_unit: str | None = None
    preparation_type: str | None = None
    citation: str | None = None
    citation_type: str | None = None


class BioLink(BaseModel):
    kind: Literal['health_effect', 'flavor', 'enzyme', 'pathway']
    id: int | None = None
    name: str
    group: str | None = None
    category: str | None = None
    gene_name: str | None = None
    uniprot_id: str | None = None
    kegg_map_id: str | None = None
    smpdb_id: str | None = None
    citation: str | None = None
    citation_type: str | None = None


class VectorResponse(BaseModel):
    food_id: int
    policy: VectorPolicy
    vector_policy: str | None = None
    similarity_policy: str | None = None
    metrics: dict[str, float | int | str | None]


class FoodComparisonResponse(BaseModel):
    food_a: FoodSummary
    food_b: FoodSummary
    policy: VectorPolicy
    similarity: float
    metric_deltas: dict[str, float]


class SimilarFood(BaseModel):
    food: FoodSummary
    similarity: float
    vector: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    count: int
    items: list[Any]
