<script lang="ts">
  import type { VectorResponse } from '$lib/api/types';
  let { vector }: { vector: VectorResponse | null } = $props();

  const preferred = [
    'p_n', 'n_compounds', 'p_mw_mean', 'p_logp_mean', 'p_tpsa_mean', 'p_hbd_mean', 'p_hba_mean',
    'q_mw_wmean', 'q_logp_wmean', 'q_tpsa_wmean', 'q_hbd_wmean', 'q_hba_wmean', 'q_num_rings_wmean'
  ];

  let metrics = $derived(vector ? preferred.filter((key) => vector.metrics[key] !== undefined && vector.metrics[key] !== null) : []);
</script>

<section class="panel-card">
  <div class="section-heading">
    <h3>Vector summary</h3>
    {#if vector}<span>{vector.policy}</span>{/if}
  </div>
  {#if vector}
    <dl class="metric-grid">
      {#each metrics as key}
        <div>
          <dt>{key.replaceAll('_', ' ')}</dt>
          <dd>{typeof vector.metrics[key] === 'number' ? Number(vector.metrics[key]).toFixed(3) : vector.metrics[key]}</dd>
        </div>
      {/each}
    </dl>
    <p class="muted-text">Similarity policy: {vector.similarity_policy ?? 'descriptor cosine'}</p>
  {:else}
    <p class="muted-text">Select a food to load descriptor statistics.</p>
  {/if}
</section>
