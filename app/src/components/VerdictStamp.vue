<template>
  <div class="stamp" :style="{ '--rot': rotation + 'deg' }">
    <svg viewBox="0 0 160 160" class="stamp-svg" aria-hidden="true">
      <circle cx="80" cy="80" r="74" class="ring" />
      <circle cx="80" cy="80" r="62" class="ring" />
      <text x="80" y="50" class="stamp-eyebrow">GHAZA COURT</text>
      <text x="80" y="86" class="stamp-word">RULED</text>
      <text x="80" y="106" class="stamp-verdict">{{ verdictLabel }}</text>
      <text x="80" y="122" class="stamp-case">No. {{ paddedId }}</text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ caseId: string; verdict: string }>();

const paddedId = computed(() => props.caseId.padStart(4, "0"));

const verdictLabel = computed(() => {
  if (props.verdict === "plaintiff") return "FOR PLAINTIFF";
  if (props.verdict === "defendant") return "FOR DEFENDANT";
  return "SPLIT DECISION";
});

// Deterministic per case so it's stable on re-render, but not identical every time.
const rotation = computed(() => {
  const n = parseInt(props.caseId, 10) || 0;
  return -10 + ((n * 7) % 10);
});
</script>

<style scoped>
.stamp {
  width: 110px;
  height: 110px;
  transform: rotate(var(--rot));
  animation: stamp-in 0.5s ease-out;
  filter: drop-shadow(0 2px 0 rgba(178, 58, 46, 0.25));
  flex-shrink: 0;
}
.stamp-svg {
  width: 100%;
  height: 100%;
}
.ring {
  fill: none;
  stroke: var(--seal);
  stroke-width: 2.5;
}
.stamp-eyebrow {
  font-family: var(--font-mono);
  font-size: 8px;
  letter-spacing: 0.08em;
  fill: var(--seal);
  text-anchor: middle;
}
.stamp-word {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 26px;
  fill: var(--seal);
  text-anchor: middle;
}
.stamp-verdict {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.05em;
  fill: var(--seal);
  text-anchor: middle;
}
.stamp-case {
  font-family: var(--font-mono);
  font-size: 9px;
  fill: var(--seal);
  text-anchor: middle;
  opacity: 0.8;
}
</style>
