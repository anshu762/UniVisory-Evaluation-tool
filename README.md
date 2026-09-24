# URIE Competition Intelligence Engine v2.0

This release replaces the generic research-only workflow with a competition-aware engine for **12 opportunities**.

## Core changes
- 12 competition profiles: IRIS National Fair, Regeneron ISEF, RSI at MIT, Conrad Challenge, The Earth Prize, Stockholm Junior Water Prize, Diamond Challenge, Blue Ocean Competition, Technovation Girls, Diana Award, GSL Global Goals Competition, Global Student Prize.
- Section 02 dynamically changes for each competition (research design, venture validation, social-impact evidence, application evidence, etc.).
- Official organiser weights are used only where verified/public; otherwise URIE internal weights are labelled as such.
- Deterministic engine calculates scores, gates and decisions; AI cannot supply the final score/decision.
- Evidence insufficiency causes abstention/holds rather than invented confidence.
- No win probability.

## Run
1. Set `OPENAI_API_KEY` in the server environment.
2. Optional: set `OPENAI_MODEL`.
3. `python server.py`
4. Open http://localhost:8000

## Files
- `competition_kb.json` — competition-specific criteria, stages, gates and source basis.
- `algorithm.py` — deterministic scoring, evidence sufficiency and decision policy.
- `engine.py` — AI orchestration + literature discovery.
- `public/index.html` — dynamic client-facing UI.

## Accuracy model
URIE is a readiness/quality evaluator, not a winner predictor. Production accuracy requires: (1) official-source versioning, (2) source retrieval/full-text review for novelty, (3) double human scoring on calibration sets, (4) inter-rater agreement measurement, and (5) competition/year-specific back-testing.

## v3 calibration + prior-art upgrade 

This build adds two safeguards before client launch:

1. **Verified-exemplar calibration.** `calibration_cases.json` stores only organizer-verifiable winner/finalist examples. `calibration.py` extracts recurring evidence patterns. Sparse competitions remain explicitly `LIMITED`/`NONE`; URIE does not invent a winner dataset or convert exemplars into win probabilities.
2. **Prior-art intelligence.** `prior_art.py` retrieves from OpenAlex + Crossref, deduplicates DOI/title records, reconstructs available abstracts, ranks textual similarity for triage, and produces a review matrix. Similarity is never itself a novelty verdict. The engine requires comparative review of problem, method, result, limitation, exact difference, and a falsification benchmark. Patent/product/code coverage is flagged as required where relevant and as `NOT_CONFIGURED` until a reliable provider is connected.

### Launch policy
UniVisory EDGE v4 is suitable for **mentor-supervised client assessment**, not autonomous winner prediction. Every output says the score is a URIE readiness score, not an official score or probability. Human review remains mandatory. For competitions without published weights, internal analytical weights remain clearly labelled.


## v4 client-report boundary
Client-facing reports intentionally stop after competition-aligned criterion strength and strongest signals. Critical gates, weaknesses, action plan, verification warnings and decision logic remain available to the mentor/backend but are not exposed to the student. The client is invited to connect with a UniVisory mentor for interpretation and next steps.
