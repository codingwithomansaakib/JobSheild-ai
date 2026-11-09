# JobShield Risk Model

The score is a heuristic engineering signal, not a probability of fraud.

Initial weights:

| Signal | Weight |
|---|---:|
| Payment request | 30 |
| Suspicious URL pattern | 20 |
| Email/domain mismatch | 15 |
| Urgency language | 10 |
| Guaranteed-job claim | 10 |

Suggested initial interpretation:

- 0-19: LOW
- 20-49: MEDIUM
- 50-100: HIGH

If insufficient information exists, use UNABLE_TO_VERIFY.

The final product should retain the individual signals and their evidence so users can understand why a level was produced.
