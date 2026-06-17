<script lang="ts">
  import CitationBadge from './CitationBadge.svelte';
  import type { CompoundFoodEdge } from '$lib/api/types';
  let { rows = [], onSelectFood }: { rows?: CompoundFoodEdge[]; onSelectFood?: (foodId: number) => void } = $props();
</script>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Food source</th>
        <th>Group</th>
        <th>Standard content</th>
        <th>Original</th>
        <th>Citation</th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row (`${row.food_id}-${row.compound_id}-${row.standard_content}-${row.citation}`)}
        <tr>
          <td><button class="link-button" type="button" onclick={() => onSelectFood?.(row.food_id)}>{row.food_name}</button></td>
          <td>{row.food_group ?? row.food_subgroup ?? '—'}</td>
          <td>{row.standard_content != null ? row.standard_content.toLocaleString() : '—'}</td>
          <td>{row.orig_content != null ? `${row.orig_content} ${row.orig_unit ?? ''}` : '—'}</td>
          <td><CitationBadge citation={row.citation} citationType={row.citation_type} /></td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
