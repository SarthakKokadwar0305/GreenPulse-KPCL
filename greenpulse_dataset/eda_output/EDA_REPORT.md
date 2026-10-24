# GreenPulse AI — EDA Summary

> All data are synthetic and do not represent actual KPCL operations.

- Energy rows: **207,360** across **8 machines**.
- Valid readings: **99.91%**.
- Total energy from valid readings: **222,791.59 kWh** (synthetic).
- Injected event labels: **9**.
- ML-ready rows after lag and rolling-window preparation: **190,609**.

## Top machines by valid energy

| Machine | Energy (kWh) |
|---|---:|
| FURN-01 | 59,046.74 |
| COMP-01 | 49,764.80 |
| COMP-02 | 39,127.17 |

## Data quality

| Status | Rows |
|---|---:|
| invalid_negative | 24 |
| missing | 72 |
| sensor_stuck | 96 |
| valid | 207,168 |

## ML split

| Split | Rows | Start | End |
|---|---:|---|---|
| test | 28,664 | 2026-09-16 07:35:00+00:00 | 2026-09-28 18:20:00+00:00 |
| train | 133,326 | 2026-07-07 18:30:00+00:00 | 2026-09-03 20:45:00+00:00 |
| validation | 28,619 | 2026-09-03 20:50:00+00:00 | 2026-09-16 07:30:00+00:00 |

## Interpretation cautions

- Use `data_quality == valid` for the primary energy baseline; inspect flagged readings separately.
- An anomaly label means a synthetic event was injected, not that a real equipment fault has been diagnosed.
- kWh per good unit can be misleading for zero-output days and different machine types.
- Carbon emissions are not calculated until verified, unit-compatible emission factors are added.
- Train/validation/test split is chronological to reduce time leakage. Fit encoders/scalers on train only.
- For next-step forecasting, only use features available at prediction time and evaluate with rolling-origin backtesting.
