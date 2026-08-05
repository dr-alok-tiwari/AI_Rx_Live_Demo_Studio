# AI Rx Live Demo Studio

AI Rx Live Demo Studio is a multipage Streamlit application for hands-on workshops with doctors and healthcare professionals. It gives participants complete prompts they can use immediately, specialty cases that reveal the limits of pattern matching, and a structured way to examine how clinical judgment changes an AI-supported decision.

The product decisions behind this release are documented in `UX_AND_PRODUCT_REVIEW.md`. The second review and publication decision are in `PUBLICATION_READINESS_REVIEW.md`; the exhaustive selector audit is recorded in `QA_INPUT_COVERAGE.md`.

The app treats AI as a supervised junior colleague. It can organise information, compare options, expose gaps, and prepare a draft. A qualified professional remains responsible for interpretation, verification, communication, and final use.

## What is included

- 101 dated tool records with official links, access notes, pricing cautions, PHI warnings, and product-status fields
- 31 complete demonstration workflows, including detailed modules for Freed, Heidi, Perplexity, NotebookLM, monday.com, and xTiles
- 323 detailed, copy-ready prompts: 17 tasks across 19 specialty lenses. Every combination generates a uniquely named, complete fictional PDF attachment, and the displayed prompt refers to that PDF instead of fill-in placeholders
- a print-ready prompt booklet in HTML and text formats for soft-copy sharing or hard-copy distribution
- 19 fictional, specialty-structured cases presented as ready prompt → simulated AI output → AI perceived diagnosis → doctor’s actual diagnosis → tacit knowledge → patient-centred action
- 120 assessment questions with answers and explanations
- 40 labelled diagnostic-interface simulations: five each for chest X-ray, brain CT, brain MRI, skin lesion, retinal image, ECG waveform, histopathology, and ultrasound
- a six-check decision-support framework, tool comparison, no-dead-end filtering, workshop planning, quiz badges, ethical social-media screening, a five-step safety gate, and a local catalogue editor
- KS Publication Pathway branding, an animated publicity asset, audience-specific invitation copy, an A4 and social programme flyer, a 13-slide facilitator deck, and a 7-slide participant recap deck
- task-based, grouped navigation; progressive case reveals; a session prompt pack; and an interactive decision-readiness checklist
- one-view desktop prompt sheets with exact copy sources, predefined input nudges, labelled nearest alternatives, and guaranteed assessment length
- one-click live-demo packages that copy the problem, objective, synthetic input, steps, attachment-ready prompt, expected output, verification checks, failure modes, and debrief questions for ChatGPT or practical labs
- a final Session Feedback page with the authorised QR code, direct-link fallback, download option, and privacy reminder
- an affiliation-neutral Developer Expertise page limited to expertise, research and teaching focus, and education

The simulation images are abstract PNG interface assets. They are not medical images and were not processed by a diagnostic model.

## Quick start

Use Python 3.12 or another version supported by the current Streamlit release.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app opens in a browser, usually at `http://localhost:8501`.

No API key is required. External tools open through their official websites. Where a live account is unavailable, the local demo workflow supplies synthetic input and an expected-output discussion.

For publication QA, run `python scripts/audit_input_matrix.py` and `python -m unittest discover -s tests -v` from the project root.

## Optional facilitator password

Facilitator Mode and Catalogue Admin are open when `FACILITATOR_PASSWORD` is not set. To protect them in a shared environment, set the variable before starting Streamlit:

```bash
export FACILITATOR_PASSWORD="choose-a-local-secret"
streamlit run app.py
```

Do not put a real password in source control. `.env.example` shows the variable name only.

## Recommended workshop flow

1. Open **Home** and frame the patient-centred path: patient need → specialty → evidence → AI support → doctor judgment → patient action.
2. Open **Prompt Library**, select a specialty and task, download the matching fictional PDF, attach it in ChatGPT, and copy the fully visible attachment-ready prompt.
3. Open **AI vs Doctor Cases**. Read the date, patient information, procedure and series before revealing the AI output.
4. Compare the AI’s perceived diagnosis with the doctor’s actual diagnosis. Ask which tacit cue or trajectory changed the decision.
5. Use **Decision Support** to apply the six checks: need, data, options, uncertainty, action, and ownership.
6. Use the relevant lab, then close with **Assessment** and one patient-centred action.
7. Open **Resource centre** for the facilitator deck, participant recap, print-ready prompt booklet, animated publicity, audience-specific copy, and programme flyers.
8. End on **Session feedback** and scan the authorised QR code. Do not enter patient-identifiable or confidential information.

Detailed delivery notes are in `FACULTY_FACILITATION_GUIDE.md`. Participants can use `PARTICIPANT_QUICK_START.md`.

## Data maintenance

Editable files are stored under `data/`:

- `tools_catalog.json`
- `demo_workflows.json`
- `prompts.json`
- `synthetic_cases.json`
- `quiz_bank.json`
- `specialties.json`
- `resources.json`
- `image_index.json`

Use **Catalogue Admin** for session edits, validation, JSON/CSV import and export, and optional URL health checks. The app does not silently overwrite the repository catalogue. Export reviewed changes, inspect the diff, run the tests, and then commit the updated file.

To rebuild the deterministic seed data and simulation assets:

```bash
python scripts/build_content.py
```

This command replaces the generated JSON and PNG seed assets. Do not use it after hand-editing those files unless you intend to regenerate them.

To rebuild the branded A4 PNG, A4 PDF, social portrait, and cropped logo derivative:

```bash
python scripts/build_flyer.py
```

The flyer script uses the committed text-free hero image and typesets all programme copy in code. The supplied session-feedback QR is kept separate from registration publicity.

## Verification

Run the local checks:

```bash
python -m unittest discover -s tests -v
python -m compileall -q .
```

If `pytest` is installed, the same test files also run with:

```bash
pytest -q
```

Tests cover catalogue schema, unique IDs, search and filtering, fallback recommendations, prompt completeness, AI-versus-Doctor case structure, downloadable workshop assets, quiz answers, navigation targets, and sample-asset counts.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and place this project at its root.
2. Confirm that `app.py`, `requirements.txt`, `.streamlit/config.toml`, `pages/`, `components/`, `data/`, and `assets/` are committed.
3. In Streamlit Community Cloud, create an app from the repository and select `app.py` as the entry point.
4. In Advanced settings, choose a supported Python version. Streamlit’s current deployment documentation lists Python 3.12 as the default at the catalogue verification date, but this can change.
5. Add `FACILITATOR_PASSWORD` through the platform’s secret or environment configuration if the facilitator areas should be restricted.
6. Deploy, open every page, run one filter with no exact match, open one local simulation image, test the flyer downloads, and verify the Session Feedback QR and direct link.

Do not add clinical API credentials or patient data to Community Cloud. Any future clinical integration requires a separate institutional security, legal, privacy, regulatory, and clinical-governance review.

## Important limitations

- The directory is curated, not exhaustive.
- A reachable official URL does not prove clinical validity, regulatory status, privacy compliance, price, or local availability.
- Product names, ownership, features, pricing, access, evidence, and regulatory status can change.
- General-purpose AI tools in this project are not presented as autonomous diagnostic or prescribing systems.
- The local risk checker uses phrase rules and cannot establish that a social post is ethical, lawful, or clinically accurate.
- The project is educational software, not a medical device or clinical record system.

Read `PRIVACY_AND_RESPONSIBLE_USE.md` before delivery and `TOOL_VERIFICATION_METHODOLOGY.md` before updating the catalogue.

## Licence

Code and project-generated synthetic assets are released under the MIT Licence. Product names and trademarks belong to their respective owners. Linked third-party material remains subject to its own terms.
