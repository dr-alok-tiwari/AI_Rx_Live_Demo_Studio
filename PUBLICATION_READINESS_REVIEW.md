# Second critical review and publication decision

Review date: 3 August 2026

## Decision

This build is ready to publish as an educational workshop application. It is not a clinical system, diagnostic device, prescribing tool, or substitute for institutional review. That boundary is stated in the interface and remains the main condition on publication.

## Findings from the second review

| Area reviewed | Finding | Resolution | Status |
|---|---|---|---|
| Prompt visibility | Removing the code-block scrollbar had shifted the problem to page-level scrolling. A detailed prompt still did not behave like a single readable object. | Detailed prompts now use a balanced three-column desktop sheet. A one-click control copies the entire exact prompt without opening a second scrolling panel. | Passed |
| Live-demo filters | Three category-and-level combinations had no exact workflow and could leave the demonstration selector empty. | The resolver now returns clearly labelled nearest workflows and keeps their actual category and level visible. | Passed |
| Directory filters | Highly restrictive combinations often have no truthful exact record. | Every finite combination returns either exact records or labelled alternatives. Each alternative reports how many selected criteria it matches. The app does not present a near match as an exact one. | Passed |
| Prompt filters | Structured task-and-specialty combinations were complete, but arbitrary free-text searches could return nothing. | A ranked, labelled prompt fallback handles unmatched text. Five common prompt-search nudges are available beside free entry. | Passed |
| Assessment length | A user could request 10, 15, or 20 questions from a six-question category. The interface then displayed fewer questions than requested. | Short category sets are supplemented with clearly disclosed questions from other safety categories until the requested count is reached. | Passed |
| Facilitator planning | Clearing the demonstration multiselect produced an empty workshop plan. | A predefined duration-based sequence remains visible until the facilitator selects replacements. Blank poll options also receive a disclosed starter set. | Passed |
| Blank free-text inputs | Several pages assumed that users already knew what to type. | Predefined nudges now sit beside directory search, prompt search, social-media screening, and reflection fields. Users can still type their own input. | Passed |
| Interaction clarity | Fallback results were available in some places but the reason for the fallback was not always visible. | Exact matches, nearest alternatives, supplemented outputs, and input nudges now use distinct messages. | Passed |

## Input-state evidence

The automated matrix audit covers every finite selection state exposed by the main workshop controls. It checked 1,314,546 states in total. No tested state produced an empty or underfilled output.

- Tool directory: 1,312,200 combinations; 21,400 exact states and 1,290,800 labelled fallback states.
- Guided start: 1,368 combinations.
- Live demonstrations: 36 category-and-level combinations, including three labelled fallbacks.
- Prompt library: 360 task-and-specialty combinations plus an unmatched free-text case.
- Case library: 20 specialty states.
- Assessment: 84 category-and-length combinations.
- Facilitator plan: 456 duration, specialty, and objective combinations.
- Problem routes, diagnostic modalities, and audience resources: 21 additional states.

The fallback count in the directory is high because the audit deliberately combines every restrictive property, including access type, pricing, specialty, technical level, demo access, India availability, and maximum time. Many such combinations do not describe a real product. Returning a labelled alternative is safer than inventing a matching tool.

## Publication conditions and known limits

- The one-view prompt sheet is designed for the desktop workshop layout. On narrow screens, the columns become a single readable stream; page scrolling is retained rather than shrinking clinical text to an unsafe size.
- Tool availability, price, access, regulation, and evidence can change. Catalogue dates and verification cautions must remain visible.
- Synthetic cases require qualified review before teaching use.
- Free-text searches cannot have a finite exhaustive test. An unmatched-string test confirms that the fallback remains non-empty and labelled.
- “At least one output” means one useful, disclosed result. It does not mean that an impossible filter combination is silently treated as an exact match.

## Final publication gate

The navigation, prompt use, fallback behaviour, nudges, assessment length, facilitator recovery, safety language, downloadable resources, and developer profile are coherent. The automated suite, route rendering, interaction tests, server health check, input matrix, identifier scan, ZIP integrity check, and presentation overflow checks must all pass on the packaged build. Subject to those repeatable checks, no publication blocker remains.
