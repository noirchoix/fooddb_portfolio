<script lang="ts">
  import type { SimilarFood } from '$lib/api/types';
  let { rows = [], onSelectFood }: { rows?: SimilarFood[]; onSelectFood?: (foodId: number) => void } = $props();
</script>

<div class="table-wrap compact">
  <table>
    <thead>
      <tr><th>Similar food</th><th>Score</th><th>Group</th></tr>
    </thead>
    <tbody>
      {#each rows as row (row.food.food_id)}
        <tr>
          <td><button class="link-button" type="button" onclick={() => onSelectFood?.(row.food.food_id)}>{row.food.name}</button></td>
          <td>{row.similarity.toFixed(4)}</td>
          <td>{row.food.food_group ?? '—'}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
