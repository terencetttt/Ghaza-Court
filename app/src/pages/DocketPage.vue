<template>
  <CaseDocket ref="docketRef" />
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import CaseDocket from "../components/CaseDocket.vue";
import { connectedAddress } from "../lib/client";

const docketRef = ref<InstanceType<typeof CaseDocket> | null>(null);

// If someone lands on /docket directly and then connects their wallet from
// the header, reload automatically rather than requiring a manual refresh.
watch(connectedAddress, (addr) => {
  if (addr) docketRef.value?.load();
});
</script>
