<template>
  <section class="card file-form">
    <div class="form-head">
      <p class="eyebrow">File a case</p>
      <p v-if="nextCaseNo !== null && nextCaseNo !== undefined" class="docket-tag mono">
        Docket entry No. {{ String(nextCaseNo).padStart(4, "0") }}
      </p>
    </div>
    <h1>Ghaza Court</h1>
    <p class="dek">
      Submit both sides of a dispute. An AI judge reads each argument, checks the open web for
      context, and rules — permanently, publicly, on Genlayer Bradbury Testnet.
    </p>

    <form @submit.prevent="submit">
      <label>
        Case title
        <input
          v-model="title"
          type="text"
          placeholder="e.g. Who actually invented the move"
          required
        />
      </label>

      <div class="grid-2">
        <label>
          Plaintiff address
          <input v-model="plaintiffAddress" type="text" class="mono" placeholder="0x…" required />
        </label>
        <span class="vs-badge mono" aria-hidden="true">v.</span>
        <label>
          Defendant address
          <input v-model="defendantAddress" type="text" class="mono" placeholder="0x…" required />
        </label>
      </div>

      <div class="grid-2">
        <label>
          Plaintiff's argument
          <textarea v-model="plaintiffArgument" rows="5" class="ruled" required></textarea>
        </label>
        <span class="vs-badge mono" aria-hidden="true">v.</span>
        <label>
          Defendant's argument
          <textarea v-model="defendantArgument" rows="5" class="ruled" required></textarea>
        </label>
      </div>

      <div class="actions">
        <button
          v-if="!address"
          type="button"
          class="primary"
          @click="connect"
          :disabled="connecting"
        >
          {{ connecting ? "Connecting…" : "Connect wallet to file" }}
        </button>
        <button v-else type="submit" class="primary" :disabled="filing">
          {{ filing ? statusMessage : "Submit to the court" }}
        </button>
        <span v-if="address" class="connected mono">{{ shortAddress }}</span>
      </div>
      <p class="fine-print">Filed publicly and permanently — there is no edit after a ruling.</p>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successId" class="success">
        Case No. {{ successId.padStart(4, "0") }} has been ruled. Opening the docket…
      </p>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { connectWallet, fileCase, connectedAddress, refreshCaseCount } from "../lib/client";

const props = defineProps<{ nextCaseNo?: number | null }>();
const emit = defineEmits<{ filed: [] }>();

const title = ref("");
const plaintiffAddress = ref("");
const plaintiffArgument = ref("");
const defendantAddress = ref("");
const defendantArgument = ref("");

const address = connectedAddress;
const connecting = ref(false);
const filing = ref(false);
const errorMessage = ref("");
const successId = ref("");
const statusMessage = ref("Filing…");

const shortAddress = computed(() => {
  const a = address.value;
  if (!a) return "";
  return `${a.slice(0, 6)}…${a.slice(-4)}`;
});

async function connect() {
  connecting.value = true;
  errorMessage.value = "";
  try {
    await connectWallet();
  } catch (err: any) {
    errorMessage.value = err?.message ?? "Could not connect wallet.";
  } finally {
    connecting.value = false;
  }
}

async function submit() {
  errorMessage.value = "";
  successId.value = "";
  filing.value = true;
  statusMessage.value = "Filing the case…";

  const deliberatingTimer = setTimeout(() => {
    statusMessage.value = "The court is deliberating (can take 3–5 minutes on Bradbury)…";
  }, 8000);

  try {
    await fileCase({
      title: title.value,
      plaintiffAddress: plaintiffAddress.value,
      plaintiffArgument: plaintiffArgument.value,
      defendantAddress: defendantAddress.value,
      defendantArgument: defendantArgument.value,
    });
    const count = await refreshCaseCount();
    successId.value = String((count ?? 1) - 1);
    title.value = "";
    plaintiffArgument.value = "";
    defendantArgument.value = "";
    emit("filed");
  } catch (err: any) {
    errorMessage.value = err?.message ?? "The court could not process this case. Try again.";
  } finally {
    clearTimeout(deliberatingTimer);
    filing.value = false;
  }
}
</script>

<style scoped>
.form-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}
.docket-tag {
  font-size: 11px;
  color: var(--seal);
  opacity: 0.8;
}
.file-form h1 {
  font-family: var(--font-display);
  font-size: 32px;
  margin: 4px 0 8px;
}
.dek {
  color: #4b4a3f;
  font-size: 15px;
  line-height: 1.55;
  margin-bottom: 24px;
}
form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: #4b4a3f;
}
input,
textarea {
  border: 1px solid var(--parchment-line);
  background: #fffdf8;
  border-radius: var(--radius);
  padding: 10px 12px;
  font-size: 14px;
  color: var(--charcoal);
  resize: vertical;
}
input.mono {
  font-size: 13px;
  letter-spacing: 0.01em;
}
textarea.ruled {
  background-image: repeating-linear-gradient(
    to bottom,
    transparent 0,
    transparent 22px,
    var(--parchment-line) 22px,
    var(--parchment-line) 23px
  );
  background-position: 0 4px;
  line-height: 23px;
  padding-top: 4px;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 14px;
  align-items: start;
}
.vs-badge {
  width: 26px;
  height: 26px;
  margin-top: 26px;
  border-radius: 50%;
  border: 1.5px solid var(--seal);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--seal);
  background: #fffdf8;
  flex-shrink: 0;
}
.actions {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 4px;
}
.primary {
  background: var(--seal);
  color: var(--parchment);
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: var(--radius);
  padding: 12px 22px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.01em;
  transition: transform 0.1s ease;
}
.primary:active:not(:disabled) {
  transform: scale(0.97);
}
.primary:disabled {
  opacity: 0.6;
  cursor: wait;
}
.connected {
  font-size: 13px;
  color: #6b6a5d;
}
.fine-print {
  font-size: 12px;
  color: #8a8772;
  margin: -2px 0 0;
}
.error {
  color: var(--seal);
  font-size: 13px;
}
.success {
  color: #3a6b3a;
  font-size: 13px;
}

@media (max-width: 560px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
  .vs-badge {
    margin: 2px auto;
  }
}
</style>
