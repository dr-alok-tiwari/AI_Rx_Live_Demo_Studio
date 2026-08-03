# Tool-verification methodology

## Scope

The catalogue is a dated workshop directory, not a procurement list or clinical evidence review. Its purpose is to help a facilitator explain workflow fit, public access, limitations, and verification questions.

## Verification date

The seed catalogue was checked on 3 August 2026. Each record stores its own `last_verified` field so later changes can be reviewed individually.

## Source hierarchy

Use the current official product page first. For regulatory information, prefer the regulator’s database or an exact official regulatory page for the named product and version. Peer-reviewed primary studies and systematic reviews are needed for clinical performance. Vendor case studies and marketing statements may describe a product but are not treated as independent clinical evidence.

## What a URL check establishes

A successful check establishes only that an official-looking destination was reachable and corresponded to the named product or company on the check date. It does not establish price, free access, India availability, privacy compliance, security, evidence quality, device clearance, intended use, or institutional suitability.

Automated checks can fail because of sign-in walls, bot protection, redirects, timeouts, or regional routing. A failure is recorded for manual review rather than silently treated as a dead product.

## Product identity changes

When ownership or branding changes, retain the workshop-recognisable name and add the current official destination. In this release, Annalise.ai redirects to Harrison.ai. Caption Health is represented through GE HealthCare’s current Caption AI and Vscan material. These notes prevent a historical product name from being presented as a current standalone destination.

## Pricing

Record an exact price only when a current official page clearly displays it, including the original currency and check date. Do not infer regional taxes, institutional discounts, exchange rates, or India pricing. Use “Not independently verified” when a sales contact, account, plan selection, or geography-specific quote is required. Prices may change.

## Regulation and evidence

Do not write “approved” at company level. Record the exact product, version, indication, geography, and regulator. If any component is missing, retain a verification warning. Keep evidence status separate from regulatory status: a legal market authorisation does not by itself show effectiveness in every population or workflow.

## Update procedure

1. Open the record in Catalogue Admin or edit `data/tools_catalog.json` directly.
2. Open the official URL and confirm product identity.
3. Check access, pricing, geography, intended user, input, output, limitations, privacy statements, evidence, and exact device status as separate fields.
4. Add source URLs that directly support any positive claim.
5. Replace unsupported wording with “Not independently verified.”
6. Set `last_verified` to the actual check date.
7. Export or save the reviewed catalogue.
8. Run `python -m unittest discover -s tests -v` and inspect the Git diff before committing.

## Current source notes

The catalogue uses official product pages for the linked tools. Specific notes with stronger claims include the Doximity Scribe official page for its stated U.S. eligibility, the Freed official page for its displayed starting price and vendor security statements, Qure.ai’s regulatory page for named U.S. FDA 510(k)-cleared variants, GE HealthCare’s Caption AI product announcement, and Streamlit’s deployment documentation. These sources should be rechecked before the next workshop.
