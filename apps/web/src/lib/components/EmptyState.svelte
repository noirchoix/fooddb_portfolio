<script lang="ts">
  let { title = 'No results yet', detail = 'Run a search to populate this panel.' }: { title?: string; detail?: string } = $props();
</script>

<div class="empty-state">
  <strong>{title}</strong>
  <p>{detail}</p>
</div>
