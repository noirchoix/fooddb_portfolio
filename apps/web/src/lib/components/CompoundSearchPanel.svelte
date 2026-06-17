<script lang="ts">
  import type { CompoundSummary } from '$lib/api/types';
  let {
    results = [],
    loading = false,
    onSearch,
    onSelect
  }: {
    results?: CompoundSummary[];
    loading?: boolean;
    onSearch: (query: string) => void;
    onSelect: (compound: CompoundSummary) => void;
  } = $props();

  let query = $state('quercetin');
</script>

<form class="search-form" onsubmit={(event) => { event.preventDefault(); onSearch(query); }}>
  <label for="compound-search">Search compounds</label>
  <div class="input-row">
    <input id="compound-search" bind:value={query} placeholder="quercetin, luteolin, apigenin…" />
    <button type="submit" disabled={loading}>{loading ? 'Searching' : 'Search'}</button>
  </div>
</form>

<div class="result-list">
  {#each results as compound (compound.compound_id)}
    <button class="result-item" type="button" onclick={() => onSelect(compound)}>
      <strong>{compound.name}</strong>
      <span>{compound.klass ?? compound.superklass ?? compound.public_id}</span>
    </button>
  {/each}
</div>
