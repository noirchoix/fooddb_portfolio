<script lang="ts">
  let { citation, citationType }: { citation?: string | null; citationType?: string | null } = $props();
</script>

{#if citation || citationType}
  <span class="citation-badge" title={citation ?? citationType ?? ''}>{citationType ?? 'citation'}{citation ? ` · ${citation}` : ''}</span>
{:else}
  <span class="citation-badge muted">No citation</span>
{/if}
