#!/usr/bin/env python3
"""EDA and chronological ML preparation for GreenPulse AI synthetic dataset.
All inputs are synthetic and do not represent KPCL measurements.
"""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def main(data_dir: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    energy = pd.read_csv(data_dir/'machine_energy.csv', parse_dates=['timestamp'])
    prod = pd.read_csv(data_dir/'production.csv', parse_dates=['production_date'])
    fuel = pd.read_csv(data_dir/'fuel_consumption.csv')
    tariffs = pd.read_csv(data_dir/'electricity_tariffs.csv')
    factors = pd.read_csv(data_dir/'emission_factors.csv')
    labels = pd.read_csv(data_dir/'anomaly_labels.csv', parse_dates=['start_time','end_time_exclusive'])

    # Ensure tz-aware datetimes (CSV timestamps preserve +05:30 offset).
    energy['timestamp'] = pd.to_datetime(energy['timestamp'], utc=True)
    labels['start_time'] = pd.to_datetime(labels['start_time'], utc=True)
    labels['end_time_exclusive'] = pd.to_datetime(labels['end_time_exclusive'], utc=True)
    energy['local_date'] = energy['timestamp'].dt.tz_convert('Asia/Kolkata').dt.date.astype(str)
    energy['hour'] = energy['timestamp'].dt.tz_convert('Asia/Kolkata').dt.hour
    energy['day_of_week'] = energy['timestamp'].dt.tz_convert('Asia/Kolkata').dt.dayofweek
    energy['is_weekend'] = energy['day_of_week'] >= 5

    # Event-level truth label, independent of the model features.
    energy['anomaly_label'] = 0
    for _, ev in labels.iterrows():
        mask = (energy.machine_id.eq(ev.machine_id) &
                energy.timestamp.ge(ev.start_time) & energy.timestamp.lt(ev.end_time_exclusive))
        energy.loc[mask, 'anomaly_label'] = 1

    # Data-quality report.
    quality_counts = energy['data_quality'].value_counts(dropna=False).sort_index()
    quality = pd.DataFrame({'data_quality': quality_counts.index, 'rows': quality_counts.values})
    quality['pct_of_all_rows'] = quality['rows'] / len(energy) * 100
    quality.to_csv(out_dir/'data_quality_summary.csv', index=False)

    # Machine-wise energy summary: only quality=valid is included in consumption totals.
    valid = energy[energy.data_quality.eq('valid')].copy()
    machine = valid.groupby(['machine_id','process_type'], as_index=False).agg(
        valid_readings=('energy_kwh','count'), total_energy_kwh=('energy_kwh','sum'),
        mean_power_kw=('average_power_kw','mean'), max_power_kw=('average_power_kw','max'),
        mean_energy_kwh_per_interval=('energy_kwh','mean'))
    machine['total_energy_kwh'] = machine['total_energy_kwh'].round(2)
    machine['mean_power_kw'] = machine['mean_power_kw'].round(3)
    machine['max_power_kw'] = machine['max_power_kw'].round(3)
    machine.to_csv(out_dir/'machine_energy_summary.csv', index=False)

    # Daily and hourly patterns. Valid readings only.
    daily = valid.groupby(['local_date','machine_id'], as_index=False).energy_kwh.sum()
    daily.to_csv(out_dir/'daily_energy_by_machine.csv', index=False)
    hourly = valid.groupby(['hour','machine_id'], as_index=False).agg(
        mean_power_kw=('average_power_kw','mean'), energy_kwh=('energy_kwh','sum'))
    hourly.to_csv(out_dir/'hourly_pattern_by_machine.csv', index=False)
    plant_daily = valid.groupby('local_date', as_index=False).energy_kwh.sum().rename(columns={'energy_kwh':'plant_energy_kwh'})
    plant_daily.to_csv(out_dir/'plant_daily_energy.csv', index=False)

    # Production efficiency; merge daily production with valid daily energy.
    daily_energy_machine = valid.groupby(['local_date','machine_id'], as_index=False).energy_kwh.sum()
    daily_prod = prod.copy()
    daily_prod['local_date'] = daily_prod['production_date'].dt.strftime('%Y-%m-%d')
    p = daily_prod.groupby(['local_date','machine_id'], as_index=False)[['units_produced','good_units']].sum()
    efficiency = daily_energy_machine.merge(p, on=['local_date','machine_id'], how='left')
    efficiency['kwh_per_good_unit'] = np.where(efficiency.good_units > 0,
                                                efficiency.energy_kwh / efficiency.good_units, np.nan)
    efficiency['kwh_per_good_unit'] = efficiency['kwh_per_good_unit'].round(4)
    efficiency.to_csv(out_dir/'production_efficiency_by_day.csv', index=False)
    efficiency_summary = efficiency.groupby('machine_id', as_index=False).agg(
        days_with_energy=('energy_kwh','count'), total_energy_kwh=('energy_kwh','sum'),
        total_units=('units_produced','sum'), total_good_units=('good_units','sum'))
    efficiency_summary['overall_kwh_per_good_unit'] = np.where(
        efficiency_summary.total_good_units > 0,
        efficiency_summary.total_energy_kwh / efficiency_summary.total_good_units, np.nan)
    efficiency_summary.to_csv(out_dir/'production_efficiency_summary.csv', index=False)

    # Chart 1: machine-wise total valid energy.
    fig, ax = plt.subplots(figsize=(10, 6))
    mplot = machine.sort_values('total_energy_kwh')
    ax.barh(mplot.machine_id, mplot.total_energy_kwh)
    ax.set_title('Machine-wise energy consumption (valid readings only)')
    ax.set_xlabel('Energy (kWh)'); ax.set_ylabel('Machine ID'); ax.grid(axis='x', alpha=.25)
    fig.tight_layout(); fig.savefig(out_dir/'01_machine_energy_consumption.png', dpi=160); plt.close(fig)

    # Chart 2: plant daily time series.
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(pd.to_datetime(plant_daily.local_date), plant_daily.plant_energy_kwh, linewidth=1.2)
    ax.set_title('Daily plant energy consumption')
    ax.set_xlabel('Date'); ax.set_ylabel('Energy (kWh)'); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(out_dir/'02_daily_plant_energy.png', dpi=160); plt.close(fig)

    # Chart 3: average power by hour.
    pivot = hourly.pivot(index='hour', columns='machine_id', values='mean_power_kw')
    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(ax=ax)
    ax.set_title('Average machine power by hour of day')
    ax.set_xlabel('Local hour (Asia/Kolkata)'); ax.set_ylabel('Mean power (kW)')
    ax.grid(alpha=.25); ax.legend(title='Machine', ncol=2, fontsize=8)
    fig.tight_layout(); fig.savefig(out_dir/'03_hourly_power_patterns.png', dpi=160); plt.close(fig)

    # Chart 4: quality flags.
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(quality.data_quality.astype(str), quality.rows)
    ax.set_title('Data-quality status counts'); ax.set_ylabel('Rows')
    ax.tick_params(axis='x', rotation=20); ax.grid(axis='y', alpha=.25)
    fig.tight_layout(); fig.savefig(out_dir/'04_data_quality_counts.png', dpi=160); plt.close(fig)

    # Chart 5: anomaly windows for affected machines, plot data +/- 12h around each event.
    selected = labels[labels.event_id.isin(['EVT-001','EVT-002','EVT-003','EVT-004','EVT-005','EVT-006'])]
    fig, axes = plt.subplots(len(selected), 1, figsize=(12, 2.6*len(selected)), sharex=False)
    if len(selected) == 1: axes = [axes]
    for ax, (_, ev) in zip(axes, selected.iterrows()):
        before = ev.start_time - pd.Timedelta(hours=12)
        after = ev.end_time_exclusive + pd.Timedelta(hours=12)
        sub = energy[(energy.machine_id == ev.machine_id) & energy.timestamp.between(before, after)].copy()
        x = sub.timestamp.dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        ax.plot(x, sub.average_power_kw, linewidth=1, label='Power reading')
        ax.axvspan(ev.start_time.tz_convert('Asia/Kolkata').tz_localize(None),
                   ev.end_time_exclusive.tz_convert('Asia/Kolkata').tz_localize(None), alpha=.2, label='Injected event')
        ax.set_title(f"{ev.event_id}: {ev.machine_id} — {ev.event_type}")
        ax.set_ylabel('kW'); ax.grid(alpha=.2); ax.legend(loc='upper right', fontsize=8)
    fig.suptitle('Synthetic energy anomaly windows (not real factory incidents)', y=1.002)
    fig.tight_layout(); fig.savefig(out_dir/'05_anomaly_event_windows.png', dpi=160, bbox_inches='tight'); plt.close(fig)

    # Chart 6: production efficiency on days with positive output.
    effplot = efficiency[efficiency.good_units > 0]
    fig, ax = plt.subplots(figsize=(11, 6))
    for mid, g in effplot.groupby('machine_id'):
        if g.kwh_per_good_unit.notna().any():
            ax.scatter(g.good_units, g.kwh_per_good_unit, s=12, alpha=.45, label=mid)
    ax.set_title('Daily energy intensity versus good units produced')
    ax.set_xlabel('Good units produced per day'); ax.set_ylabel('kWh per good unit')
    ax.grid(alpha=.25); ax.legend(title='Machine', ncol=2, fontsize=8)
    fig.tight_layout(); fig.savefig(out_dir/'06_production_efficiency.png', dpi=160); plt.close(fig)

    # ML-ready features. Use valid rows only; target is next interval's average power per machine.
    # Split on unique timestamps chronologically (70/15/15), never random split.
    # Keep the complete time grid while creating lags: invalid sensor rows become
    # NaN, so lag_1 really means the previous 5-minute interval rather than the
    # previous available valid row. Rows around sensor faults are dropped later.
    clean = energy.copy().sort_values(['machine_id','timestamp'])
    clean['power_kw'] = clean['average_power_kw'].where(clean['data_quality'].eq('valid'))
    clean['energy_kwh'] = clean['energy_kwh'].where(clean['data_quality'].eq('valid'))
    for lag in [1,2,3,6,12,288,2016]:
        clean[f'power_lag_{lag}'] = clean.groupby('machine_id')['power_kw'].shift(lag)
    clean['rolling_mean_1h'] = clean.groupby('machine_id')['power_kw'].transform(lambda s: s.shift(1).rolling(12, min_periods=12).mean())
    clean['rolling_std_1h'] = clean.groupby('machine_id')['power_kw'].transform(lambda s: s.shift(1).rolling(12, min_periods=12).std())
    clean['hour_sin'] = np.sin(2*np.pi*clean.hour/24)
    clean['hour_cos'] = np.cos(2*np.pi*clean.hour/24)
    clean['dow_sin'] = np.sin(2*np.pi*clean.day_of_week/7)
    clean['dow_cos'] = np.cos(2*np.pi*clean.day_of_week/7)
    clean['target_power_next_interval_kw'] = clean.groupby('machine_id')['power_kw'].shift(-1)
    feature_cols = ['machine_id','timestamp','hour','day_of_week','is_weekend','rated_power_kw',
                    'machine_state','shift','ambient_temp_c','power_kw','energy_kwh',
                    'power_lag_1','power_lag_2','power_lag_3','power_lag_6','power_lag_12',
                    'power_lag_288','power_lag_2016','rolling_mean_1h','rolling_std_1h',
                    'hour_sin','hour_cos','dow_sin','dow_cos','target_power_next_interval_kw']
    ml = clean[feature_cols].dropna().copy()
    ts = ml.timestamp.sort_values().drop_duplicates().reset_index(drop=True)
    t1 = ts.iloc[int(len(ts)*0.70)]
    t2 = ts.iloc[int(len(ts)*0.85)]
    ml['split'] = np.where(ml.timestamp < t1, 'train', np.where(ml.timestamp < t2, 'validation', 'test'))
    # Use one combined file and separate files for convenient model training.
    ml.to_csv(out_dir/'ml_features_all.csv', index=False)
    for split in ['train','validation','test']:
        ml[ml.split.eq(split)].to_csv(out_dir/f'ml_{split}.csv', index=False)
    split_summary = ml.groupby('split', as_index=False).agg(rows=('timestamp','size'),
        start_timestamp=('timestamp','min'), end_timestamp=('timestamp','max'), machines=('machine_id','nunique'))
    split_summary.to_csv(out_dir/'ml_split_summary.csv', index=False)

    # Compact findings report.
    top = machine.sort_values('total_energy_kwh', ascending=False).head(3)
    q_counts = {str(k): int(v) for k,v in quality_counts.items()}
    report = {
      'dataset_type':'synthetic only; not KPCL measurements',
      'input_energy_rows':int(len(energy)), 'unique_machines':int(energy.machine_id.nunique()),
      'start_timestamp_local':str(energy.timestamp.min().tz_convert('Asia/Kolkata')),
      'end_timestamp_local':str(energy.timestamp.max().tz_convert('Asia/Kolkata')),
      'data_quality_counts':q_counts,
      'valid_reading_pct':round(float(energy.data_quality.eq('valid').mean()*100),4),
      'total_valid_energy_kwh':round(float(valid.energy_kwh.sum()),2),
      'machine_energy_rank_top3':[{'machine_id':r.machine_id,'energy_kwh':round(float(r.total_energy_kwh),2)} for r in top.itertuples()],
      'injected_event_count':int(len(labels)),
      'production_efficiency_note':'kWh/good unit is only meaningful on days with positive good-unit output; machine processes differ and should not be compared blindly.',
      'emissions_note':'Scope 1/2 emissions not calculated because emission_factors.csv intentionally has no verified factors.',
      'tariff_note':'Tariffs are illustrative synthetic values, not KPCL tariff data.',
      'ml_split_method':'Chronological timestamp split: 70% train, 15% validation, 15% test; valid quality rows only; lag features use past observations.',
      'ml_feature_rows':int(len(ml)),
      'split_boundaries':{'train_end_exclusive':str(t1),'validation_end_exclusive':str(t2)},
      'split_rows':{str(k):int(v) for k,v in ml.split.value_counts().items()},
      'charts':['01_machine_energy_consumption.png','02_daily_plant_energy.png','03_hourly_power_patterns.png','04_data_quality_counts.png','05_anomaly_event_windows.png','06_production_efficiency.png']
    }
    (out_dir/'eda_summary.json').write_text(json.dumps(report, indent=2))
    # Markdown summary for users.
    lines = [
      '# GreenPulse AI — EDA Summary', '',
      '> All data are synthetic and do not represent actual KPCL operations.', '',
      f"- Energy rows: **{len(energy):,}** across **{energy.machine_id.nunique()} machines**.",
      f"- Valid readings: **{report['valid_reading_pct']:.2f}%**.",
      f"- Total energy from valid readings: **{report['total_valid_energy_kwh']:,.2f} kWh** (synthetic).",
      f"- Injected event labels: **{len(labels)}**.",
      f"- ML-ready rows after lag and rolling-window preparation: **{len(ml):,}**.",
      '', '## Top machines by valid energy', '', '| Machine | Energy (kWh) |', '|---|---:|'
    ]
    for r in top.itertuples(): lines.append(f'| {r.machine_id} | {r.total_energy_kwh:,.2f} |')
    lines += ['', '## Data quality', '', '| Status | Rows |', '|---|---:|']
    for k,v in q_counts.items(): lines.append(f'| {k} | {v:,} |')
    lines += ['', '## ML split', '', '| Split | Rows | Start | End |', '|---|---:|---|---|']
    for r in split_summary.itertuples(): lines.append(f'| {r.split} | {r.rows:,} | {r.start_timestamp} | {r.end_timestamp} |')
    lines += ['', '## Interpretation cautions', '',
      '- Use `data_quality == valid` for the primary energy baseline; inspect flagged readings separately.',
      '- An anomaly label means a synthetic event was injected, not that a real equipment fault has been diagnosed.',
      '- kWh per good unit can be misleading for zero-output days and different machine types.',
      '- Carbon emissions are not calculated until verified, unit-compatible emission factors are added.',
      '- Train/validation/test split is chronological to reduce time leakage. Fit encoders/scalers on train only.',
      '- For next-step forecasting, only use features available at prediction time and evaluate with rolling-origin backtesting.', '']
    (out_dir/'EDA_REPORT.md').write_text('\n'.join(lines))
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data-dir', default='data')
    p.add_argument('--output-dir', default='eda_output')
    a=p.parse_args()
    main(Path(a.data_dir), Path(a.output_dir))
