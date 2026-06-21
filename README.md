# Ghaza Court

A public, permanent, AI-adjudicated dispute resolution dApp running on [GenLayer](https://genlayer.com)'s Bradbury Testnet.

File a dispute with both sides' arguments. An AI judge, running as a leader/validator consensus across real Bradbury validators (not a single centralized model call), pulls light web context and rules — and the ruling is written to the chain permanently. No appeals, no edits, no takedowns. Every case ever filed is publicly browsable in the docket.

## How it works

- **One write function, `file_case`.** Whoever files submits both sides' arguments in a single transaction — title, plaintiff address + argument, defendant address + argument.
- **The ruling is non-deterministic-safe.** GenLayer's validators each independently run the same judging prompt (web search + LLM call) and only need to agree on the structured `verdict` field — not on the exact wording of the reasoning, which legitimately varies between validators. This is what makes AI-generated rulings actually reach consensus on a blockchain.
- **Everything is permanent.** Once a case is ruled, there's no function to edit or delete it. The contract has no admin key.
- **Reads are free.** Browsing the docket costs no gas — only filing a new case does.

## Stack

- **Contract:** Python, GenLayer Intelligent Contracts (`gl.vm.run_nondet_unsafe` for the consensus pattern), deployed to GenLayer Bradbury Testnet.
- **Frontend:** Vue 3 + TypeScript + Vite, talking to the contract via `genlayer-js`.

## Project structure

```
internet-court/
├── internet_court.py     # the contract
├── ARCHITECTURE.md        # full system design doc
└── app/                    # the frontend (this is what gets deployed)
    ├── src/
    │   ├── pages/          # FilePage, DocketPage
    │   ├── components/     # FileCaseForm, CaseDocket, CaseCard, VerdictStamp
    │   ├── lib/client.ts   # the only file that talks to genlayer-js
    │   └── router/
    └── package.json
```

## Running locally

```bash
cd app
npm install
cp .env.example .env
# edit .env, set VITE_CONTRACT_ADDRESS to the deployed contract address
npm run dev
```

## Deployment

The contract is deployed by hand through [GenLayer Studio](https://studio.genlayer.com) (network set to **Genlayer Bradbury Testnet**). The frontend deploys to Vercel from this repo — see the deployment notes for the exact steps, since Vercel's Root Directory needs to point at `app/`, not the repo root.

## What this isn't

This is a demo of AI-adjudicated consensus on a blockchain, not a legal system. Nothing ruled here carries any binding legal authority — it's "court" in the sense of a public, permanent record of an argument and a verdict, not a substitute for an actual court.
