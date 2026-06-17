<script lang="ts">
  import ApiStatusBadge from '$lib/components/ApiStatusBadge.svelte';
  import BioLinkDrawer from '$lib/components/BioLinkDrawer.svelte';
  import CompoundProfileCard from '$lib/components/CompoundProfileCard.svelte';
  import CompoundSearchPanel from '$lib/components/CompoundSearchPanel.svelte';
  import CompoundTable from '$lib/components/CompoundTable.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import ErrorNotice from '$lib/components/ErrorNotice.svelte';
  import FoodProfileCard from '$lib/components/FoodProfileCard.svelte';
  import FoodSearchPanel from '$lib/components/FoodSearchPanel.svelte';
  import FoodSourceTable from '$lib/components/FoodSourceTable.svelte';
  import LoadingBlock from '$lib/components/LoadingBlock.svelte';
  import SimilarityTable from '$lib/components/SimilarityTable.svelte';
  import VectorSummaryPanel from '$lib/components/VectorSummaryPanel.svelte';
  import { fooddbApi } from '$lib/api/client';
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
    VectorResponse,
    VectorPolicy
  } from '$lib/api/types';

  type Tab = 'food' | 'compound' | 'compare';

  let activeTab = $state<Tab>('food');
  let health = $state<HealthResponse | null>(null);
  let healthLoading = $state(true);
  let healthError = $state<string | null>(null);

  let error = $state<string | null>(null);
  let loading = $state(false);

  let foodResults = $state<FoodSummary[]>([]);
  let selectedFood = $state<FoodDetail | null>(null);
  let foodCompounds = $state<FoodCompoundEdge[]>([]);
  let vector = $state<VectorResponse | null>(null);
  let similarFoods = $state<SimilarFood[]>([]);

  let compoundResults = $state<CompoundSummary[]>([]);
  let selectedCompound = $state<CompoundDetail | null>(null);
  let compoundFoods = $state<CompoundFoodEdge[]>([]);
  let bioLinks = $state<BioLink[]>([]);
  let drawerOpen = $state(false);

  let compareFoodA = $state('Angelica');
  let compareFoodB = $state('Ginger');
  let vectorPolicy = $state<VectorPolicy>('zscore');
  let comparison = $state<FoodComparisonResponse | null>(null);

  async function guard(action: () => Promise<void>) {
    loading = true;
    error = null;
    try {
      await action();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unexpected request failure.';
    } finally {
      loading = false;
    }
  }

  async function loadHealth() {
    healthLoading = true;
    try {
      health = await fooddbApi.health();
    } catch (err) {
      healthError = err instanceof Error ? err.message : 'API health check failed.';
    } finally {
      healthLoading = false;
    }
  }

  async function searchFoods(query: string) {
    await guard(async () => {
      foodResults = await fooddbApi.searchFoods(query);
    });
  }

  async function selectFood(food: FoodSummary | number) {
    await guard(async () => {
      const foodId = typeof food === 'number' ? food : food.food_id;
      selectedFood = await fooddbApi.getFood(foodId);
      foodCompounds = await fooddbApi.foodCompounds(foodId, 100, false);
      vector = await fooddbApi.foodVector(foodId, vectorPolicy);
      similarFoods = await fooddbApi.similarFoods(selectedFood.name, vectorPolicy, 10);
      activeTab = 'food';
    });
  }

  async function searchCompounds(query: string) {
    await guard(async () => {
      compoundResults = await fooddbApi.searchCompounds(query);
    });
  }

  async function selectCompound(compound: CompoundSummary | number) {
    await guard(async () => {
      const compoundId = typeof compound === 'number' ? compound : compound.compound_id;
      selectedCompound = await fooddbApi.getCompound(compoundId);
      compoundFoods = await fooddbApi.compoundFoods(compoundId, 100, false);
      bioLinks = await fooddbApi.bioLinks(compoundId, 50);
      drawerOpen = true;
      activeTab = 'compound';
    });
  }

  async function compareFoods() {
    await guard(async () => {
      comparison = await fooddbApi.compareFoods(compareFoodA, compareFoodB, vectorPolicy);
    });
  }

  $effect(() => {
    loadHealth();
    searchFoods('Angelica');
    searchCompounds('quercetin');
  });
</script>

<svelte:head>
  <title>FoodDB Compound Explorer</title>
  <meta name="description" content="Search FoodDB foods, compounds, concentrations, descriptor vectors, and bio-linked metadata." />
</svelte:head>

<main class="app-shell">
  <header class="top-bar">
    <div>
      <p class="eyebrow">Computational phytochemistry suite</p>
      <h1>FoodDB Compound Explorer</h1>
      <p class="lede">Search foods and phytochemical compounds, inspect concentration evidence, compare descriptor vectors, and trace health, flavor, enzyme, and pathway links.</p>
    </div>
    <ApiStatusBadge {health} loading={healthLoading} error={healthError} />
  </header>

  <section class="workspace">
    <aside class="search-panel">
      <div class="tabs" role="tablist" aria-label="Search workspace">
        <button class:active={activeTab === 'food'} type="button" onclick={() => (activeTab = 'food')}>Food search</button>
        <button class:active={activeTab === 'compound'} type="button" onclick={() => (activeTab = 'compound')}>Compound search</button>
        <button class:active={activeTab === 'compare'} type="button" onclick={() => (activeTab = 'compare')}>Compare foods</button>
      </div>

      {#if activeTab === 'food'}
        <FoodSearchPanel results={foodResults} loading={loading} onSearch={searchFoods} onSelect={selectFood} />
      {:else if activeTab === 'compound'}
        <CompoundSearchPanel results={compoundResults} loading={loading} onSearch={searchCompounds} onSelect={selectCompound} />
      {:else}
        <form class="search-form" onsubmit={(event) => { event.preventDefault(); compareFoods(); }}>
          <label for="food-a">Food A</label>
          <input id="food-a" bind:value={compareFoodA} />
          <label for="food-b">Food B</label>
          <input id="food-b" bind:value={compareFoodB} />
          <label for="policy">Vector policy</label>
          <select id="policy" bind:value={vectorPolicy}>
            <option value="zscore">zscore</option>
            <option value="raw">raw</option>
            <option value="idf">idf</option>
          </select>
          <button type="submit" disabled={loading}>{loading ? 'Comparing' : 'Compare foods'}</button>
        </form>
      {/if}
    </aside>

    <section class="result-area">
      {#if error}<ErrorNotice message={error} />{/if}
      {#if loading}<LoadingBlock label="Querying FoodDB artifacts…" />{/if}

      {#if activeTab === 'food'}
        {#if selectedFood}
          <FoodProfileCard food={selectedFood} />
          <div class="split-grid">
            <section class="panel-card wide">
              <div class="section-heading"><h3>Compounds in {selectedFood.name}</h3><span>{foodCompounds.length} shown</span></div>
              <CompoundTable rows={foodCompounds} onSelectCompound={selectCompound} />
            </section>
            <section class="side-stack">
              <VectorSummaryPanel {vector} />
              <section class="panel-card">
                <div class="section-heading"><h3>Similar foods</h3><span>{vectorPolicy}</span></div>
                <SimilarityTable rows={similarFoods} onSelectFood={selectFood} />
              </section>
            </section>
          </div>
        {:else}
          <EmptyState title="Select a food" detail="Search for a food, then select a result to load its compounds, vector summary, and similar foods." />
        {/if}
      {:else if activeTab === 'compound'}
        {#if selectedCompound}
          <CompoundProfileCard compound={selectedCompound} />
          <section class="panel-card wide">
            <div class="section-heading"><h3>Food sources containing {selectedCompound.name}</h3><span>{compoundFoods.length} shown</span></div>
            <FoodSourceTable rows={compoundFoods} onSelectFood={selectFood} />
          </section>
        {:else}
          <EmptyState title="Select a compound" detail="Search for quercetin, luteolin, apigenin, or another compound to view food sources and bio-linked metadata." />
        {/if}
      {:else}
        {#if comparison}
          <section class="panel-card comparison-card">
            <p class="eyebrow">Descriptor-vector comparison</p>
            <h2>{comparison.food_a.name} ↔ {comparison.food_b.name}</h2>
            <div class="score-card">
              <span>Cosine similarity</span>
              <strong>{comparison.similarity.toFixed(4)}</strong>
              <small>{comparison.policy}</small>
            </div>
            <div class="delta-grid">
              {#each Object.entries(comparison.metric_deltas).slice(0, 18) as [key, value]}
                <div><span>{key.replaceAll('_', ' ')}</span><strong>{value.toFixed(3)}</strong></div>
              {/each}
            </div>
          </section>
        {:else}
          <EmptyState title="Compare two foods" detail="Enter two food names to compare their descriptor vectors using raw, zscore, or IDF policy." />
        {/if}
      {/if}
    </section>
  </section>

  <BioLinkDrawer open={drawerOpen} compound={selectedCompound} links={bioLinks} onClose={() => (drawerOpen = false)} />
</main>
