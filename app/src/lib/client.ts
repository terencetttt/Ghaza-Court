import { ref } from "vue";
import { createClient } from "genlayer-js";
import { testnetBradbury } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";

const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS as any;

export type CaseRecord = {
  case_id: string;
  title: string;
  plaintiff: string;
  plaintiff_argument: string;
  defendant: string;
  defendant_argument: string;
  filer: string;
  verdict: "plaintiff" | "defendant" | "split" | string;
  confidence: "high" | "medium" | "low" | string;
  reasoning: string;
  ruling_summary: string;
};

let client: ReturnType<typeof createClient> | null = null;

// Reactive so the header and any page can show/react to the connected
// address without re-deriving their own copy of this state.
export const connectedAddress = ref<string | null>(null);

// MetaMask/Rabby probe for Snaps support — harmless noise, not a real error.
function isSnapsNoise(err: unknown): boolean {
  const msg = String((err as any)?.message ?? err ?? "");
  return msg.includes("wallet_getSnaps");
}

export async function connectWallet(): Promise<string> {
  const eth = (window as any).ethereum;
  if (!eth) {
    throw new Error("No wallet found. Install MetaMask or Rabby to file a case.");
  }
  const accounts: string[] = await eth.request({ method: "eth_requestAccounts" });
  const addr = accounts[0] as any;

  client = createClient({ chain: testnetBradbury, account: addr });
  try {
    // Prompts the wallet to add/switch to Genlayer Bradbury Testnet if needed.
    await client.connect("testnetBradbury");
  } catch (err) {
    if (!isSnapsNoise(err)) throw err;
  }
  connectedAddress.value = addr;
  return addr;
}

export function getConnectedAddress(): string | null {
  return connectedAddress.value;
}

function requireClient() {
  // NOTE: reads also go through the connected client for now, so the docket
  // currently needs a wallet connected to load. Worth revisiting later if
  // genlayer-js supports an account-less read client for public browsing.
  if (!client) throw new Error("Connect your wallet first.");
  return client;
}

// Bradbury AI writes take real validators 3-5 minutes. ACCEPTED (not
// FINALIZED) is the status to wait for — FINALIZED times out on Bradbury.
// Retry on "Timed out" rather than giving up after one attempt.
async function waitForReceiptWithRetries(hash: `0x${string}`, maxTotalMs = 600_000) {
  const c = requireClient();
  const start = Date.now();
  let lastErr: unknown = null;
  while (Date.now() - start < maxTotalMs) {
    try {
      return await c.waitForTransactionReceipt({ hash: hash as any, status: TransactionStatus.ACCEPTED });
    } catch (err) {
      if (isSnapsNoise(err)) continue;
      const msg = String((err as any)?.message ?? "").toLowerCase();
      if (!msg.includes("timed out")) throw err;
      lastErr = err; // still deliberating — loop again
    }
  }
  throw lastErr ?? new Error("Timed out waiting for the court to rule.");
}

export async function fileCase(input: {
  title: string;
  plaintiffAddress: string;
  plaintiffArgument: string;
  defendantAddress: string;
  defendantArgument: string;
}): Promise<void> {
  const c = requireClient();
  const hash = await c.writeContract({
    address: CONTRACT_ADDRESS,
    functionName: "file_case",
    args: [
      input.title,
      input.plaintiffAddress,
      input.plaintiffArgument,
      input.defendantAddress,
      input.defendantArgument,
    ],
    value: BigInt(0),
  });
  await waitForReceiptWithRetries(hash as `0x${string}`);
}

export async function getCaseCount(): Promise<number> {
  const c = requireClient();
  const result = await c.readContract({
    address: CONTRACT_ADDRESS,
    functionName: "get_case_count",
    args: [],
  });
  return Number(result);
}

// Reactive so the header's "X rulings" count updates from anywhere a case
// gets filed, without needing to thread an event up through the router.
export const caseCount = ref<number | null>(null);

export async function refreshCaseCount(): Promise<number | null> {
  if (!connectedAddress.value) return null;
  try {
    caseCount.value = await getCaseCount();
  } catch {
    // not connected yet — leave whatever value was last known
  }
  return caseCount.value;
}

export async function getCaseIds(): Promise<string[]> {
  const c = requireClient();
  const result = await c.readContract({
    address: CONTRACT_ADDRESS,
    functionName: "get_case_ids",
    args: [],
  });
  return result as string[];
}

export async function getCase(caseId: string): Promise<CaseRecord> {
  const c = requireClient();
  const result = await c.readContract({
    address: CONTRACT_ADDRESS,
    functionName: "get_case",
    args: [caseId],
  });
  return result as CaseRecord;
}

export async function getAllCases(): Promise<CaseRecord[]> {
  const ids = await getCaseIds();
  const cases: CaseRecord[] = [];
  for (const id of ids) {
    cases.push(await getCase(id));
  }
  return cases.reverse(); // newest first
}
