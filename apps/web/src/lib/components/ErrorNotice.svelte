<script lang="ts">
  let { message }: { message: string } = $props();
</script>

<div class="error-notice" role="alert">{message}</div>
