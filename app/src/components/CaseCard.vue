<template>
  <div class="case-card">
    <button class="case-row" @click="expanded = !expanded" :aria-expanded="expanded">
      <span class="docket-no mono">No. {{ paddedId }}</span>
      <span class="case-title">{{ caseRecord.title }}</span>
      <span class="case-status mono">{{ statusLabel }}</span>
    </button>

    <div v-if="expanded" class="case-body">
      <div class="parties">
        <div class="party">
          <p class="eyebrow">Plaintiff — {{ short(caseRecord.plaintiff) }}</p>
          <p>{{ caseRecord.plaintiff_argument }}</p>
        </div>
        <div class="aisle" />
        <div class="party">
          <p class="eyebrow">Defendant — {{ short(caseRecord.defendant) }}</p>
          <p>{{ caseRecord.defendant_argument }}</p>
        </div>
      </div>

      <hr class="hairline" />

      <div class="ruling">
        <VerdictStamp :case-id="caseRecord.case_id" :verdict="caseRecord.verdict" />
        <div class="ruling-text">
          <p class="eyebrow">Confidence: {{ caseRecord.confidence }}</p>
          <p class="ruling-summary">{{ caseRecord.ruling_summary }}</p>
          <p class="reasoning">{{ caseRecord.reasoning }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { CaseRecord } from "../lib/client";
import VerdictStamp from "./VerdictStamp.vue";

const props = defineProps<{ caseRecord: CaseRecord }>();
const expanded = ref(false);

const paddedId = computed(() => props.caseRecord.case_id.padStart(4, "0"));
const statusLabel = computed(() => {
  if (props.caseRecord.verdict === "plaintiff") return "Plaintiff";
  if (props.caseRecord.verdict === "defendant") return "Defendant";
  return "Split";
});

function short(addr: string) {
  if (!addr || addr.length < 10) return addr;
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}
</script>

<style scoped>
.case-card {
  border-bottom: 1px solid var(--ink-raised);
}
.case-row {
  width: 100%;
  display: grid;
  grid-template-columns: 70px 1fr auto;
  gap: 16px;
  align-items: baseline;
  background: none;
  border: none;
  color: var(--parchment);
  padding: 16px 4px;
  text-align: left;
  font-size: 15px;
}
.docket-no {
  color: var(--brass);
  font-size: 13px;
}
.case-title {
  font-family: var(--font-display);
  font-size: 18px;
}
.case-status {
  font-size: 12px;
  letter-spacing: 0.04em;
  color: var(--slate);
}
.case-body {
  padding: 8px 4px 24px;
}
.parties {
  display: grid;
  grid-template-columns: 1fr 1px 1fr;
  gap: 20px;
  color: var(--parchment);
}
.party p {
  margin: 6px 0 0;
  line-height: 1.5;
  font-size: 14px;
}
.eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--slate);
}
.aisle {
  background: var(--brass);
  opacity: 0.4;
}
.ruling {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 20px;
  align-items: start;
}
.ruling-summary {
  font-family: var(--font-display);
  font-size: 17px;
  margin: 4px 0 8px;
}
.reasoning {
  color: var(--slate);
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 560px) {
  .parties {
    grid-template-columns: 1fr;
  }
  .aisle {
    display: none;
  }
  .ruling {
    grid-template-columns: 1fr;
  }
}
</style>
