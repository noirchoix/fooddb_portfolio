<script lang="ts">
  import type { BioLink, CompoundDetail } from '$lib/api/types';
  let { open = false, compound = null, links = [], onClose }: { open?: boolean; compound?: CompoundDetail | null; links?: BioLink[]; onClose: () => void } = $props();

  let grouped = $derived(links.reduce<Record<string, BioLink[]>>((acc, link) => {
    acc[link.kind] = [...(acc[link.kind] ?? []), link];
    return acc;
  }, {}));
</script>

{#if open}
  <aside class="drawer" aria-label="Compound details">
    <div class="drawer-header">
      <div>
        <p class="eyebrow">Bio-linked metadata</p>
        <h2>{compound?.name ?? 'Compound detail'}</h2>
      </div>
      <button type="button" class="ghost" onclick={onClose}>Close</button>
    </div>

    {#if compound}
      <dl class="meta-grid one-col">
        <div><dt>InChIKey</dt><dd>{compound.inchikey ?? '—'}</dd></div>
        <div><dt>SMILES</dt><dd class="breakable">{compound.smiles ?? '—'}</dd></div>
        <div><dt>Class</dt><dd>{compound.kingdom ?? '—'} / {compound.superklass ?? '—'} / {compound.klass ?? '—'}</dd></div>
      </dl>
    {/if}

    {#each Object.entries(grouped) as [kind, items]}
      <section class="drawer-section">
        <h3>{kind.replace('_', ' ')}</h3>
        {#each items as item (`${kind}-${item.id}-${item.name}`)}
          <article class="link-card">
            <strong>{item.name}</strong>
            <span>{item.group ?? item.category ?? item.gene_name ?? item.kegg_map_id ?? item.uniprot_id ?? ''}</span>
            {#if item.citation}<small>{item.citation}</small>{/if}
          </article>
        {/each}
      </section>
    {:else}
      <p class="muted-text">No health, flavor, enzyme, or pathway links found for this compound.</p>
    {/each}
  </aside>
{/if}
