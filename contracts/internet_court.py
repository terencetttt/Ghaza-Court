# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

# THE INTERNET COURT
# A public, permanent, AI-adjudicated dispute resolution contract.
# Built for deployment on GenLayer Bradbury Testnet (not the free Studio Network).
#
# Architecture (see ARCHITECTURE.md for the full plan):
#   - One write function, file_case. Whoever files submits BOTH sides' arguments
#     in a single transaction — no separate "respond" step.
#   - The AI judge reads both arguments, pulls light web context on the case
#     title, and returns a verdict + reasoning.
#   - Consensus uses gl.vm.run_nondet_unsafe with a custom leader/validator pair,
#     NOT gl.eq_principle.strict_eq. strict_eq fails consensus on LLM calls
#     because LLM output is inherently non-deterministic even with strict JSON
#     formatting — confirmed directly from GenLayer's own docs. Validators only
#     need to agree on the structured `verdict` field; reasoning and summary
#     text are taken from the leader as-is, since wording legitimately varies.
#   - Every case and ruling is stored permanently — there is no edit/delete path.

from genlayer import *
from dataclasses import dataclass
import typing


@allow_storage
@dataclass
class Case:
    case_id: str
    title: str
    plaintiff: str
    plaintiff_argument: str
    defendant: str
    defendant_argument: str
    filer: str
    verdict: str          # "plaintiff" | "defendant" | "split"
    confidence: str        # "high" | "medium" | "low"
    reasoning: str
    ruling_summary: str


class InternetCourt(gl.Contract):
    case_counter: u256
    cases: TreeMap[str, Case]
    case_ids: DynArray[str]

    def __init__(self):
        self.case_counter = u256(0)

    @gl.public.write
    def file_case(
        self,
        title: str,
        plaintiff_address: str,
        plaintiff_argument: str,
        defendant_address: str,
        defendant_argument: str,
    ) -> str:
        filer = str(gl.message.sender_address)
        case_id = str(int(self.case_counter))

        def leader_fn():
            # --- pull light web context on the dispute topic ---
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={title}"
                response = gl.nondet.web.get(search_url)
                web_context = response.body.decode("utf-8")[:3000]
            except Exception:
                web_context = "No web context available."

            prompt = f"""You are an impartial AI judge presiding over a case filed with the Internet Court — a public, permanent, AI-adjudicated ruling system.

CASE TITLE: {title}

PLAINTIFF'S ARGUMENT:
{plaintiff_argument}

DEFENDANT'S ARGUMENT:
{defendant_argument}

RELEVANT WEB CONTEXT (may be noisy or incomplete, use your judgment):
{web_context}

Weigh both sides fairly. Consider factual accuracy, the strength of evidence presented, and the web context where it's actually relevant. Reach a clear verdict — avoid "split" unless the case is genuinely a wash.

Return a JSON object with these exact keys:
- "verdict": one of "plaintiff", "defendant", "split"
- "confidence": one of "high", "medium", "low"
- "reasoning": 2-4 sentences explaining the ruling
- "ruling_summary": one sentence, suitable for a public case record"""

            result = gl.nondet.exec_prompt(prompt, response_format="json")
            if not isinstance(result, dict) or "verdict" not in result:
                # Malformed output — raise so the validator disagrees and a
                # new leader is rotated in, rather than silently storing junk.
                raise gl.vm.UserError(f"Malformed ruling from LLM: {result}")

            verdict = str(result.get("verdict", "")).strip().lower()
            if verdict not in ("plaintiff", "defendant", "split"):
                verdict = "split"

            return {
                "verdict": verdict,
                "confidence": str(result.get("confidence", "low")).strip().lower(),
                "reasoning": str(result.get("reasoning", "")),
                "ruling_summary": str(result.get("ruling_summary", "")),
            }

        def validator_fn(leaders_res) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            my_result = leader_fn()
            # Only the structured verdict needs exact agreement — reasoning
            # and summary wording will legitimately vary between validators.
            return my_result["verdict"] == leaders_res.calldata["verdict"]

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        case = Case(
            case_id=case_id,
            title=title,
            plaintiff=plaintiff_address,
            plaintiff_argument=plaintiff_argument,
            defendant=defendant_address,
            defendant_argument=defendant_argument,
            filer=filer,
            verdict=result["verdict"],
            confidence=result["confidence"],
            reasoning=result["reasoning"],
            ruling_summary=result["ruling_summary"],
        )

        self.cases[case_id] = case
        self.case_ids.append(case_id)
        self.case_counter = u256(int(self.case_counter) + 1)

        return case_id

    @gl.public.view
    def get_case(self, case_id: str) -> typing.Any:
        if case_id not in self.cases:
            return {}
        case = self.cases[case_id]
        return {
            "case_id": case.case_id,
            "title": case.title,
            "plaintiff": case.plaintiff,
            "plaintiff_argument": case.plaintiff_argument,
            "defendant": case.defendant,
            "defendant_argument": case.defendant_argument,
            "filer": case.filer,
            "verdict": case.verdict,
            "confidence": case.confidence,
            "reasoning": case.reasoning,
            "ruling_summary": case.ruling_summary,
        }

    @gl.public.view
    def get_case_count(self) -> int:
        return int(self.case_counter)

    @gl.public.view
    def get_case_ids(self) -> typing.Any:
        return [cid for cid in self.case_ids]

    @gl.public.view
    def get_all_cases(self) -> typing.Any:
        return [self.get_case(cid) for cid in self.case_ids]
