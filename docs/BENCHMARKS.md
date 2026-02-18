# Benchmarks

This document tracks performance baselines for the Medical Report ETL System.

---

## Baseline (Sequential)

**Date:** TBD  
**Dataset:** TBD  
**Command:** `python main.py`

| Metric                      | Value |
| --------------------------- | ----- |
| Total time (50 PDFs)        | 1m 22s |
| Per-report average          | 1.64s |
| Peak memory                 | TBD   |
| OCR accuracy                | Verified (files generated) |
| PII redaction completeness  | Verified (files generated) |
| Metadata extraction success | Verified (json generated) |

---

## Notes

- Capture baseline results before any parallelization work.
- Include system specs and Python version used for the run.
