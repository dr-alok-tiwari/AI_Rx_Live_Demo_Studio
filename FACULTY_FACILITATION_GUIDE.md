# Faculty facilitation guide

## Purpose and boundary

AI Rx Live Demo Studio supports an executive workshop for doctors. It is designed for live teaching, not clinical care. Use fictional cases, abstract image simulations, openly licensed material, or documents that participants are authorised to share. Do not invite participants to test a tool with a real prescription, report, recording, patient photograph, or identifiable note.

State the operating principle at the start: patient first, doctor led, AI assisted. The clinician checks the source, the output, the evidence, and the final use.

## Prepare before the session

1. Run `python -m unittest discover -s tests -v` and start the app locally.
2. Open each external tool that you intend to show. Product access, sign-in requirements, and free limits can change without notice.
3. Use the synthetic input supplied in the selected workflow. Keep a local screenshot or expected-output discussion ready if the service is slow or unavailable.
4. Decide whether the group will see Facilitator Mode. Set `FACILITATOR_PASSWORD` if the app will run on a shared host.
5. Confirm the venue’s internet, projector resolution, browser zoom, audio policy, and rules for recording participants.
6. Review the current institutional policy on AI, privacy, information security, copyright, consent, and clinical governance.
7. Download the facilitator deck and programme flyer from **Resource centre**, and keep the participant recap ready for sharing.
8. Print the prompt booklet, or share its HTML/text version before the practical section. Participants should not have to design prompts during the workshop.
9. Open **Session feedback** and test the authorised QR code before participants arrive. Remind the group not to submit patient-identifiable or confidential information.

## Opening script

“Today we will use AI to draft, organise, compare, and explain. We will not ask it to make an autonomous clinical decision. Every case is fictional. Please do not upload a patient name, image, report, prescription, voice recording, identifier, or confidential institutional document. We will examine what the tool gets wrong as carefully as what it gets right. Our north star is the patient; our comparison is AI support versus clinical judgment.”

## 30-minute route

- 4 minutes: opening boundary and five-step safety gate
- 6 minutes: plain-language patient communication
- 7 minutes: Perplexity PICO evidence orientation
- 9 minutes: Heidi or Freed synthetic documentation workflow
- 4 minutes: risk recap and one-question reflection

## 60-minute route

- 7 minutes: safety gate and confidence poll
- 8 minutes: patient communication
- 12 minutes: clinical documentation
- 10 minutes: Perplexity evidence workflow
- 10 minutes: NotebookLM journal-club synthesis
- 8 minutes: ethical professional post
- 5 minutes: assessment and next action

## 90-minute clinical decision lab

- 10 minutes: patient need, boundaries, and decision question
- 15 minutes: download the matching fictional PDF, attach it in ChatGPT, and copy the complete specialty prompt
- 25 minutes: ready prompt → AI output → AI perceived diagnosis versus doctor’s actual diagnosis
- 15 minutes: apply the six decision-support checks
- 15 minutes: transfer the same structure to small specialty groups
- 10 minutes: one patient-centred action, assessment, and take-home downloads

## How to run a demonstration

1. Name the patient need and the decision before naming the product.
2. Show the document date, patient information, procedure information, and series or trajectory.
3. Open the complete prompt in **Prompt Library**. Download its uniquely named fictional PDF, attach the PDF in ChatGPT, and copy the full attachment-ready prompt without altering the safety clauses.
4. Read the privacy checkpoint aloud, then generate or simulate the output.
5. Ask one participant to state the AI’s perceived diagnosis and cite the evidence it used.
6. Reveal the doctor’s actual diagnosis. Ask which tacit cue, missing context, or change over time altered the interpretation.
7. Trace each material statement to the source. Mark unsupported additions, omissions, contradictions, and lost uncertainty.
8. Apply the six checks: need, data, options, uncertainty, action, and ownership.
9. Finish with a safe, understandable patient action and the clinician-verification checklist.

## Keep the case specific enough to teach, broad enough to transfer

The case should make one clinical insight visible, but it should not imply that the same prompt or diagnosis fits every doctor or setting. After the debrief, ask participants what would change in their specialty, patient population, local policy, and available evidence. The app includes a generalisation note for every case for this reason.

## Consent and publicity

Keep consent content literature-only: published guidance, institution-approved templates, and plain-language teaching notes. Do not turn the workshop into case-specific legal advice, and do not use real consent records.

Use the audience copy in the **Resource centre** rather than sending one generic message. Doctors, hospital leaders, educators, researchers, and life-science audiences have different reasons to care. The same page includes the animated invitation and both workshop decks.

## Handling common workshop moments

If a tool fails to load, use the local workflow, synthetic input, and expected-output section. The teaching objective is the supervision process, not a flawless vendor demonstration.

If a participant offers a real record, stop the upload. Explain that removing a name may not be sufficient because dates, images, locations, rare conditions, and free text can identify someone.

If the output looks excellent, slow down. Ask the group to check the smallest facts: dose, unit, date, side, negation, duration, and who said what. Fluent wording can hide a material error.

If participants ask whether a product is “approved,” identify the exact product, version, intended use, indication, country, and regulator. The catalogue deliberately uses “Not independently verified” where those details were not confirmed.

## Assessment

Use confidence ratings only as reflection. The completion badges are workshop markers, not credentials. A strong debrief asks participants to name:

- one task that AI may accelerate;
- one failure they will actively check;
- one institutional approval they need;
- one action that must remain under direct professional control.

## After the session

Export the workshop plan and record which demonstrations ran. Note any broken URL or materially changed product information. Update the catalogue only after checking an official source and recording the verification date. Do not retain participant prompts or outputs if they contain sensitive or unauthorised information.
