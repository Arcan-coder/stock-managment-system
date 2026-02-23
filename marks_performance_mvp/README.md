# Marks Performance MVP

A lightweight MVP to track marks, compare against targets, identify weak/strong subjects, and generate weekly actions.

## What it does
- Reads assessments (`Subject`, `Assessment Type`, `Date`, `Score`, `Total`, `Weight`)
- Computes weighted average marks per subject
- Compares actuals against target marks
- Flags trend as `improving`, `declining`, or `steady`
- Finds the weakest assessment type in each subject
- Generates a weekly tracker table:
  - `Week`, `Subject`, `Avg Marks`, `Target`, `Progress`, `Next Action`
- Optionally creates charts if `matplotlib` is installed:
  - `marks_trend.png`
  - `avg_vs_target.png`

## Run
```bash
python marks_performance_mvp/marks_mvp.py \
  --assessments marks_performance_mvp/data/assessments.csv \
  --targets marks_performance_mvp/data/targets.csv \
  --outdir marks_performance_mvp/output
```

## Output
- `marks_performance_mvp/output/summary.txt`
- `marks_performance_mvp/output/weekly_tracker.csv`
- charts (optional, depending on matplotlib availability)

## Notes
- Biology can have a lower target (e.g., 70%) while other subjects target A/B ranges.
- For weekly focus, start with the largest subject gap and weakest assessment type.
