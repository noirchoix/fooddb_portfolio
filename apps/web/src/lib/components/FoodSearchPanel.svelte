<script lang="ts">
  import type { FoodSummary } from '$lib/api/types';
  let {
    results = [],
    loading = false,
    onSearch,
    onSelect
  }: {
    results?: FoodSummary[];
    loading?: boolean;
    onSearch: (query: string) => void;
    onSelect: (food: FoodSummary) => void;
  } = $props();

  let query = $state('Angelica');
</script>

<form class="search-form" onsubmit={(event) => { event.preventDefault(); onSearch(query); }}>
  <label for="food-search">Search foods</label>
  <div class="input-row">
    <input id="food-search" bind:value={query} placeholder="Angelica, ginger, cabbage…" />
    <button type="submit" disabled={loading}>{loading ? 'Searching' : 'Search'}</button>
  </div>
</form>

<div class="result-list">
  {#each results as food (food.food_id)}
    <button class="result-item" type="button" onclick={() => onSelect(food)}>
      <strong>{food.name}</strong>
      <span>{food.name_scientific ?? food.food_group ?? food.public_id}</span>
    </button>
  {/each}
</div>
