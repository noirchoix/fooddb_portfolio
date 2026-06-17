<script lang="ts">
  import type { CompoundDetail, CompoundSummary } from '$lib/api/types';
  let { compound }: { compound: CompoundSummary | CompoundDetail | null } = $props();
</script>

{#if compound}
  <article class="profile-card">
    <div>
      <p class="eyebrow">Compound profile</p>
      <h2>{compound.name}</h2>
      {#if compound.public_id}<p class="muted-text">{compound.public_id}</p>{/if}
    </div>
    <dl class="meta-grid">
      <div><dt>Compound ID</dt><dd>{compound.compound_id}</dd></div>
      <div><dt>CAS</dt><dd>{compound.cas_number ?? '—'}</dd></div>
      <div><dt>Mass</dt><dd>{compound.moldb_mono_mass?.toFixed(3) ?? '—'}</dd></div>
      <div><dt>Class</dt><dd>{compound.klass ?? compound.superklass ?? '—'}</dd></div>
    </dl>
    {#if compound.inchikey}<p class="mono-line">{compound.inchikey}</p>{/if}
    {#if 'description' in compound && compound.description}
      <p class="description">{compound.description}</p>
    {/if}
  </article>
{/if}
