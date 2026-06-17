<script lang="ts">
  import type { HealthResponse } from '$lib/api/types';
  type Props = { health: HealthResponse | null; loading?: boolean; error?: string | null };
  let { health, loading = false, error = null }: Props = $props();
</script>

<div class="status-badge" class:ok={health?.ok} class:error={error} aria-live="polite">
  {#if loading}
    Checking API…
  {:else if error}
    API unavailable
  {:else if health?.ok}
    Data online · {health.foods.toLocaleString()} foods · {health.compounds.toLocaleString()} compounds
  {:else}
    API status unknown
  {/if}
</div>
