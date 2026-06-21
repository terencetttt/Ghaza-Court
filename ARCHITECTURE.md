# The Internet Court — Architectural Plan

A public, permanent, AI-adjudicated dispute resolution dApp on GenLayer Bradbury Testnet.

This document describes the full system shape — backend contract and frontend — before any code is written. It supersedes the inline explanation given earlier in this build; treat this as the source of truth going forward.

---

## 1. System overview

Two independent pieces, deployed separately, connected only by a contract address:

1. **Backend** — one Intelligent Contract (`internet_court.py`), deployed once to GenLayer Bradbury Testnet through the Studio web IDE. It owns all state and all logic. It never changes after deployment unless redeployed.
2. **Frontend** — a Vue 3 + TypeScript single-page app, built with Vite, that talks to the deployed contract through the `genlayer-js` SDK. It owns no state of its own — every piece of data it shows comes from a read call to the contract.

There is no traditional backend server, no database, and no API layer in between. The frontend talks directly to the GenLayer network; the GenLayer network's validators talk directly to the LLM and the open web when ruling on a case.

---

## 2. Backend — the Intelligent Contract

### 2.1 Purpose

Take both sides of a dispute, have an AI judge weigh them (with light web context), and permanently record a verdict that anyone can read. One core write function; no edit or delete path anywhere.

### 2.2 State

Three pieces of contract storage:

- `case_counter` (`u256`) — total number of cases filed, doubles as the next case ID.
- `cases` (`TreeMap[str, Case]`) — every case record, keyed by case ID.
- `case_ids` (`DynArray[str]`) — case IDs in filing order, for listing/browsing.

`Case` is a `@allow_storage @dataclass` holding: `case_id`, `title`, `plaintiff` address, `plaintiff_argument`, `defendant` address, `defendant_argument`, `filer` address, `verdict`, `confidence`, `reasoning`, `ruling_summary`.

### 2.3 The one write function — `file_case`

Signature: `file_case(title, plaintiff_address, plaintiff_argument, defendant_address, defendant_argument) -> case_id`.

Whoever calls this submits **both** sides' arguments in a single transaction — there is no separate "respond" step. This is a deliberate simplicity tradeoff: it keeps the contract to one write function, at the cost of an honesty assumption (whoever files could misrepresent the other side). A true adversarial-filing version would split this into two write functions with a "pending response" status — out of scope for this version.

Inside the function, the AI judgment runs through GenLayer's **leader/validator consensus pattern**, not `strict_eq`:

1. **`leader_fn()`** — does a light web search on the case title (DuckDuckGo HTML endpoint, no auth needed), builds a judge prompt containing both arguments plus that web context, and calls the LLM with `response_format="json"`. It validates the result has a `verdict` key and raises an error if not (forcing a leader rotation rather than silently storing junk). It normalizes `verdict` to one of `plaintiff` / `defendant` / `split`.
2. **`validator_fn(leaders_res)`** — every other validator independently re-runs `leader_fn()` and checks **only** that their own `verdict` matches the leader's. Reasoning, confidence, and summary text are allowed to vary in wording between validators — only the structured verdict needs exact agreement. This is the fix for a real bug found earlier: `gl.eq_principle.strict_eq` does not work with LLM calls because LLM output is inherently non-deterministic even with strict JSON formatting; GenLayer's own docs confirm this explicitly.
3. `gl.vm.run_nondet_unsafe(leader_fn, validator_fn)` ties the two together and returns the agreed-upon result once consensus is reached.

Once consensus is reached, a `Case` record is built and stored permanently — no further mutation possible.

### 2.4 Read functions (free, no gas)

- `get_case(case_id) -> dict` — single case lookup.
- `get_case_count() -> int`
- `get_case_ids() -> list[str]`
- `get_all_cases() -> list[dict]` — every case, newest-relevant ordering left to the caller.

### 2.5 Deployment

Deployed by hand through `studio.genlayer.com`: load the `.py` file, switch the network selector to **Genlayer Bradbury Testnet** (not the default free Studio Network), confirm the (empty) constructor inputs, deploy. The resulting address is the only thing the frontend needs to know about the backend.

---

## 3. Frontend — the Vue app

### 3.1 Purpose

Give a human a way to connect a wallet, file a case, and browse the public docket of rulings — nothing else.

### 3.2 Component structure

- **`App.vue`** — page shell. Shows a live "in session" indicator and a live case count (read from the contract), and lays out the filing form above the docket.
- **`FileCaseForm.vue`** — the only way to write to the contract. Connect-wallet button, four text fields (two addresses, two arguments) plus a title field, a submit button that shows progressive status ("filing…" → "the court is deliberating, this can take 3–5 minutes on Bradbury…").
- **`CaseDocket.vue`** — fetches and lists every case. Each row collapsed by default, expandable.
- **`CaseCard.vue`** — one case, expanded: both arguments side by side, then the AI's reasoning and a verdict stamp.
- **`VerdictStamp.vue`** — the one deliberate visual flourish: a rotated wax-seal-style "RULED" stamp showing the verdict and case number, used inside `CaseCard`.

### 3.3 Contract communication — `lib/client.ts`

This is the only file that imports `genlayer-js`. Everything else in the app calls functions exported from here; nothing else talks to the network directly.

- `connectWallet()` — requests accounts from the injected wallet (MetaMask/Rabby), creates a `genlayer-js` client pointed at `testnetBradbury`, calls `client.connect("testnetBradbury")` (this is what prompts the wallet to add/switch networks).
- `fileCase({...})` — calls `writeContract` with `functionName: "file_case"`, then waits for the receipt.
- Waiting for the receipt uses `TransactionStatus.ACCEPTED` (not `FINALIZED`, which times out on Bradbury) wrapped in a retry loop — Bradbury's real AI-driven writes take 3–5 minutes, and a single `waitForTransactionReceipt` call without retries will give up too early.
- `getCase`, `getCaseCount`, `getCaseIds`, `getAllCases` — thin wrappers around `readContract` matching the four contract view functions.
- A known simplification, not yet resolved: reads currently also require a connected wallet client, even though view calls don't need signing. Worth revisiting once the rest is confirmed working.

### 3.4 Build and deploy

Vite + Vue 3 + TypeScript. `VITE_CONTRACT_ADDRESS` is the one environment variable the build needs — it's the address copied out of Studio after deploying the backend. Locally: `npm install`, set `.env`, `npm run dev`. For a real deploy: push to GitHub, import into Vercel, set the Root Directory to the frontend folder, set the same environment variable in Vercel's project settings.

---

## 4. End-to-end flow

1. Person opens the site, clicks "connect wallet" → MetaMask prompts to add/switch to Bradbury.
2. Person fills out the filing form (title, both addresses, both arguments) and submits → this is a single `file_case` write transaction.
3. On the network: a leader validator runs the web-search-plus-LLM judging step; every other validator independently re-runs the same prompt and checks agreement on just the verdict field; once they agree, the transaction is accepted and the case is written to contract storage permanently.
4. The frontend, which has been polling for the receipt, sees `ACCEPTED`, re-reads the new case, and refreshes the docket.
5. Anyone (with a connected wallet, per the current simplification) can browse the docket and expand any case to see both arguments and the full ruling.

---

## 5. What's deliberately out of scope for this version

- No adversarial two-step filing (one party files, the other responds before ruling).
- No public read access without a connected wallet.
- No appeal mechanism (GenLayer's protocol has a native appeal process at the network level, but this contract doesn't surface it in the UI).
- No legal-disclaimer footer yet — worth adding before this goes anywhere public, since GenLayer's own docs caution against literal "court" framing implying binding legal authority.
