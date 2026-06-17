export type VectorPolicy = 'raw' | 'zscore' | 'idf';

export type HealthResponse = {
  ok: boolean;
  database_path: string;
  curated_dir: string;
  foods: number;
  compounds: number;
  curated_edges: number;
  vector_rows: number;
  available_policies: string[];
  qc_ok?: boolean | null;
};

export type FoodSummary = {
  food_id: number;
  public_id?: string | null;
  name: string;
  name_scientific?: string | null;
  food_group?: string | null;
  food_subgroup?: string | null;
  food_type?: string | null;
  category?: string | null;
  ncbi_taxonomy_id?: number | null;
};

export type FoodDetail = FoodSummary & {
  description?: string | null;
  wikipedia_id?: string | null;
};

export type CompoundSummary = {
  compound_id: number;
  public_id?: string | null;
  name: string;
  cas_number?: string | null;
  inchikey?: string | null;
  inchi?: string | null;
  smiles?: string | null;
  moldb_mono_mass?: number | null;
  kingdom?: string | null;
  superklass?: string | null;
  klass?: string | null;
  subklass?: string | null;
};

export type CompoundDetail = CompoundSummary & {
  description?: string | null;
  annotation_quality?: string | null;
};

export type FoodCompoundEdge = {
  food_id: number;
  compound_id: number;
  compound_name?: string | null;
  inchikey?: string | null;
  presence?: number | null;
  standard_content?: number | null;
  orig_content?: number | null;
  orig_unit?: string | null;
  orig_min?: number | null;
  orig_max?: number | null;
  preparation_type?: string | null;
  citation?: string | null;
  citation_type?: string | null;
};

export type CompoundFoodEdge = {
  food_id: number;
  food_name: string;
  food_group?: string | null;
  food_subgroup?: string | null;
  compound_id: number;
  standard_content?: number | null;
  orig_content?: number | null;
  orig_unit?: string | null;
  preparation_type?: string | null;
  citation?: string | null;
  citation_type?: string | null;
};

export type BioLink = {
  kind: 'health_effect' | 'flavor' | 'enzyme' | 'pathway';
  id?: number | null;
  name: string;
  group?: string | null;
  category?: string | null;
  gene_name?: string | null;
  uniprot_id?: string | null;
  kegg_map_id?: string | null;
  smpdb_id?: string | null;
  citation?: string | null;
  citation_type?: string | null;
};

export type VectorResponse = {
  food_id: number;
  policy: VectorPolicy;
  vector_policy?: string | null;
  similarity_policy?: string | null;
  metrics: Record<string, number | string | null>;
};

export type SimilarFood = {
  food: FoodSummary;
  similarity: number;
  vector: Record<string, number | string | null>;
};

export type FoodComparisonResponse = {
  food_a: FoodSummary;
  food_b: FoodSummary;
  policy: VectorPolicy;
  similarity: number;
  metric_deltas: Record<string, number>;
};
