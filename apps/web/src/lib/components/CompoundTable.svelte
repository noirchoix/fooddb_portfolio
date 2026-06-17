<script lang="ts">
  import CitationBadge from './CitationBadge.svelte';
  import type { FoodCompoundEdge } from '$lib/api/types';
  let { rows = [], onSelectCompound }: { rows?: FoodCompoundEdge[]; onSelectCompound?: (compoundId: number) => void } = $props();
</script>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Compound</th>
        <th>Standard content</th>
        <th>Original</th>
        <th>Preparation</th>
        <th>Citation</th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row (`${row.food_id}-${row.compound_id}-${row.compound_name}-${row.standard_content}`)}
        <tr>
          <td>
            <button class="link-button" type="button" onclick={() => onSelectCompound?.(row.compound_id)}>{row.compound_name ?? row.compound_id}</button>
            {#if row.inchikey}<small>{row.inchikey}</small>{/if}
          </td>
          <td>{row.standard_content != null ? row.standard_content.toLocaleString() : '—'}</td>
          <td>{row.orig_content != null ? `${row.orig_content} ${row.orig_unit ?? ''}` : '—'}</td>
          <td>{row.preparation_type ?? '—'}</td>
          <td><CitationBadge citation={row.citation} citationType={row.citation_type} /></td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
