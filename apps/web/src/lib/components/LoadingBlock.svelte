<script lang="ts">
  let { label = 'Loading…' }: { label?: string } = $props();
</script>

<div class="loading-block" role="status">{label}</div>
