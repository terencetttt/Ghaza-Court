<template>
  <section>
    <div class="docket-header">
      <h2>The Docket</h2>
      <button class="refresh" @click="load" :disabled="loading">
        {{ loading ? "Loading…" : "Refresh" }}
      </button>
    </div>

    <p v-if="error" class="empty">{{ error }}</p>
    <p v-else-if="!loading && cases.length === 0" class="empty">
      No cases filed yet. The court is in session —
      <RouterLink to="/">file the first one</RouterLink>.
    </p>

    <div v-else>
      <CaseCard v-for="c in cases" :key="c.case_id" :case-record="c" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getAllCases, getConnectedAddress, type CaseRecord } from "../lib/client";
import CaseCard from "./CaseCard.vue";

const cases = ref<CaseRecord[]>([]);
const loading = ref(false);
const error = ref("");

async function load() {
  if (!getConnectedAddress()) {
    error.value = "Connect your wallet to view the docket.";
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    cases.value = await getAllCases();
  } catch (err: any) {
    error.value = err?.message ?? "Could not load the docket.";
  } finally {
    loading.value = false;
  }
}

defineExpose({ load });
onMounted(load);
</script>

<style scoped>
.docket-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}
.docket-header h2 {
  font-family: var(--font-display);
  font-size: 22px;
  margin: 0;
}
.refresh {
  background: none;
  border: 1px solid var(--slate);
  color: var(--parchment);
  border-radius: var(--radius);
  padding: 6px 12px;
  font-size: 13px;
}
.empty {
  color: var(--slate);
  font-size: 14px;
  padding: 24px 0;
}
</style>
