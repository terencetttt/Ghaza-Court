<template>
  <header class="top">
    <span class="wordmark mono">GHAZA COURT</span>
    <div class="top-right">
      <span class="session">
        <span class="dot" /> in session
        <span v-if="caseCount !== null" class="count mono"> · {{ caseCount }} rulings</span>
      </span>
      <button v-if="!connectedAddress" class="connect mono" @click="connect" :disabled="connecting">
        {{ connecting ? "Connecting…" : "Connect wallet" }}
      </button>
      <span v-else class="address mono">{{ shortAddress }}</span>
    </div>
  </header>

  <nav class="pages mono">
    <RouterLink to="/" exact-active-class="active">File a case</RouterLink>
    <RouterLink to="/docket" exact-active-class="active">Browse the docket</RouterLink>
  </nav>

  <RouterView />

  <footer class="foot mono">Genlayer Bradbury Testnet · permanent, public, AI-ruled</footer>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from "vue";
import { connectWallet, connectedAddress, caseCount, refreshCaseCount } from "./lib/client";

const connecting = ref(false);

const shortAddress = computed(() => {
  const a = connectedAddress.value;
  if (!a) return "";
  return `${a.slice(0, 6)}…${a.slice(-4)}`;
});

async function connect() {
  connecting.value = true;
  try {
    await connectWallet();
  } catch {
    // FileCaseForm surfaces connection errors inline; the header button
    // just stays in its "Connect wallet" state if this fails.
  } finally {
    connecting.value = false;
  }
}

watch(connectedAddress, (addr) => {
  if (addr) refreshCaseCount();
});

onMounted(refreshCaseCount);
</script>

<style scoped>
.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.top-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.wordmark {
  font-size: 13px;
  letter-spacing: 0.12em;
  color: var(--brass);
}
.session {
  font-size: 12px;
  color: var(--slate);
  display: flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4caf6e;
  animation: pulse-dot 1.8s ease-in-out infinite;
}
.count {
  color: var(--brass);
}
.connect {
  background: none;
  border: 1px solid var(--brass);
  color: var(--brass);
  border-radius: var(--radius);
  padding: 6px 12px;
  font-size: 12px;
}
.connect:disabled {
  opacity: 0.6;
  cursor: wait;
}
.address {
  font-size: 12px;
  color: var(--slate);
}
.pages {
  display: flex;
  gap: 20px;
  margin: 24px 0 32px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(242, 236, 221, 0.12);
}
.pages a {
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--slate);
  text-decoration: none;
  padding-bottom: 4px;
  border-bottom: 2px solid transparent;
}
.pages a.active {
  color: var(--brass);
  border-bottom-color: var(--seal);
}
.foot {
  margin-top: 48px;
  text-align: center;
  font-size: 11px;
  letter-spacing: 0.06em;
  color: var(--slate);
}
</style>
