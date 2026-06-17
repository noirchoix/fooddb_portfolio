import type {
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
  VectorResponse
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const API_PREFIX = `${API_BASE_URL}/api/v1/fooddb`;

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`);
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      message = body?.detail?.message ?? body?.detail ?? message;
    } catch {
      // keep default message
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

const qs = (value: string) => encodeURIComponent(value.trim());

export const fooddbApi = {
  health: () => request<HealthResponse>('/health'),
  searchFoods: (query: string, limit = 20) => request<FoodSummary[]>(`/foods/search?q=${qs(query)}&limit=${limit}`),
  resolveFood: (query: string) => request<FoodSummary>(`/foods/resolve?q=${qs(query)}`),
  getFood: (foodId: number) => request<FoodDetail>(`/foods/${foodId}`),
  foodCompounds: (foodId: number, limit = 100, measuredOnly = false) =>
    request<FoodCompoundEdge[]>(`/foods/${foodId}/compounds?limit=${limit}&measured_only=${measuredOnly}`),
  foodVector: (foodId: number, policy: VectorPolicy = 'zscore') =>
    request<VectorResponse>(`/foods/${foodId}/vector?policy=${policy}`),
  similarFoods: (query: string, policy: VectorPolicy = 'zscore', topK = 10) =>
    request<SimilarFood[]>(`/foods/similar?q=${qs(query)}&policy=${policy}&top_k=${topK}`),
  compareFoods: (foodA: string, foodB: string, policy: VectorPolicy = 'zscore') =>
    request<FoodComparisonResponse>(`/foods/compare?food_a=${qs(foodA)}&food_b=${qs(foodB)}&policy=${policy}`),
  searchCompounds: (query: string, limit = 20) => request<CompoundSummary[]>(`/compounds/search?q=${qs(query)}&limit=${limit}`),
  getCompound: (compoundId: number) => request<CompoundDetail>(`/compounds/${compoundId}`),
  compoundFoods: (compoundId: number, limit = 100, measuredOnly = false) =>
    request<CompoundFoodEdge[]>(`/compounds/${compoundId}/foods?limit=${limit}&measured_only=${measuredOnly}`),
  bioLinks: (compoundId: number, limitPerKind = 50) =>
    request<BioLink[]>(`/compounds/${compoundId}/bio-links?limit_per_kind=${limitPerKind}`)
};
