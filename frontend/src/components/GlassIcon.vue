<template>
  <svg class="gicon" aria-hidden="true">
    <use :href="`#i-${name}`" />
  </svg>
</template>

<script setup lang="ts">
defineProps<{ name: string }>()
</script>
