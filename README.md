# Makara

Makara is an automated pipeline designed to run in multiple machines aiming to construct a full dataset of perf stats executions of different programs.

## Dependencies

- GCC
- Python 3.x
- Linux perf

## How to execute

```bash
python3 collect_data.py
```

It will compile and execute all programs, generating a results folder and a zip at the end.
