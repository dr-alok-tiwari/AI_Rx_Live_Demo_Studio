# User-input coverage audit

Run the audit from the project root:

```bash
python scripts/audit_input_matrix.py
```

The current audited result is:

| Interface | Finite states checked | Exact or normal output | Labelled fallback | Empty or underfilled |
|---|---:|---:|---:|---:|
| Tool directory | 1,312,200 | 21,400 | 1,290,800 | 0 |
| Guided start | 1,368 | 1,368 | 0 | 0 |
| Live demonstrations | 36 | 33 | 3 | 0 |
| Prompt library | 361 | 360 | 1 | 0 |
| Case library | 20 | 20 | 0 | 0 |
| Assessment | 84 | 84 | 0 | 0 |
| Facilitator plan | 456 | 456 | 0 | 0 |
| Problem routes | 8 | 8 | 0 | 0 |
| Diagnostic simulations | 8 | 8 | 0 | 0 |
| Audience resources | 5 | 5 | 0 | 0 |

The directory audit uses every finite selector value. Free text is unbounded, so it is tested separately with a deliberately unmatched search. That search returns labelled alternatives rather than an empty page.

