<script lang="ts">
  import type { FoodDetail, FoodSummary } from '$lib/api/types';
  let { food }: { food: FoodSummary | FoodDetail | null } = $props();
</script>

{#if food}
  <article class="profile-card">
    <div>
      <p class="eyebrow">Food profile</p>
      <h2>{food.name}</h2>
      {#if food.name_scientific}<p class="italic">{food.name_scientific}</p>{/if}
    </div>
    <dl class="meta-grid">
      <div><dt>FoodDB ID</dt><dd>{food.public_id ?? food.food_id}</dd></div>
      <div><dt>Group</dt><dd>{food.food_group ?? '—'}</dd></div>
      <div><dt>Subgroup</dt><dd>{food.food_subgroup ?? '—'}</dd></div>
      <div><dt>Category</dt><dd>{food.category ?? '—'}</dd></div>
    </dl>
    {#if 'description' in food && food.description}
      <p class="description">{food.description}</p>
    {/if}
  </article>
{/if}
