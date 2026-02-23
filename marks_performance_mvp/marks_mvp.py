#!/usr/bin/env python3
"""Marks Performance MVP

Usage:
  python marks_performance_mvp/marks_mvp.py \
    --assessments marks_performance_mvp/data/assessments.csv \
    --targets marks_performance_mvp/data/targets.csv \
    --outdir marks_performance_mvp/output
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Assessment:
    subject: str
    assessment_type: str
    date: datetime
    score: float
    total: float
    weight: float

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.score / self.total) * 100


def read_assessments(path: Path) -> List[Assessment]:
    assessments: List[Assessment] = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"Subject", "Assessment Type", "Date", "Score", "Total", "Weight"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing assessment columns: {', '.join(sorted(missing))}")

        for row in reader:
            assessments.append(
                Assessment(
                    subject=row["Subject"].strip(),
                    assessment_type=row["Assessment Type"].strip(),
                    date=datetime.strptime(row["Date"].strip(), "%Y-%m-%d"),
                    score=float(row["Score"]),
                    total=float(row["Total"]),
                    weight=float(row["Weight"]),
                )
            )
    return assessments


def read_targets(path: Path) -> Dict[str, float]:
    targets: Dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"Subject", "Target"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing target columns: {', '.join(sorted(missing))}")
        for row in reader:
            targets[row["Subject"].strip()] = float(row["Target"])
    return targets


def weighted_average(values: List[Tuple[float, float]]) -> float:
    total_weight = sum(weight for _, weight in values)
    if total_weight == 0:
        return 0.0
    return sum(percent * weight for percent, weight in values) / total_weight


def subject_averages(assessments: List[Assessment]) -> Dict[str, float]:
    grouped: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
    for item in assessments:
        grouped[item.subject].append((item.percent, item.weight))
    return {subject: weighted_average(values) for subject, values in grouped.items()}


def subject_trends(assessments: List[Assessment]) -> Dict[str, str]:
    grouped: Dict[str, List[Assessment]] = defaultdict(list)
    for item in assessments:
        grouped[item.subject].append(item)

    trends: Dict[str, str] = {}
    for subject, items in grouped.items():
        ordered = sorted(items, key=lambda x: x.date)
        if len(ordered) < 3:
            trends[subject] = "steady"
            continue

        split = len(ordered) // 2
        first_half = [x.percent for x in ordered[:split]]
        second_half = [x.percent for x in ordered[split:]]
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        diff = second_avg - first_avg
        if diff > 2:
            trends[subject] = "improving"
        elif diff < -2:
            trends[subject] = "declining"
        else:
            trends[subject] = "steady"
    return trends


def weakest_assessment_types(assessments: List[Assessment]) -> Dict[str, str]:
    by_subject_type: Dict[Tuple[str, str], List[Tuple[float, float]]] = defaultdict(list)
    for item in assessments:
        by_subject_type[(item.subject, item.assessment_type)].append((item.percent, item.weight))

    by_subject: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    for (subject, assessment_type), values in by_subject_type.items():
        by_subject[subject].append((assessment_type, weighted_average(values)))

    weakest: Dict[str, str] = {}
    for subject, items in by_subject.items():
        items_sorted = sorted(items, key=lambda x: x[1])
        weakest[subject] = items_sorted[0][0]
    return weakest


def build_weekly_tracker(
    assessments: List[Assessment],
    targets: Dict[str, float],
    weakest_types: Dict[str, str],
) -> List[Dict[str, str]]:
    weekly_data: Dict[Tuple[int, str], List[Tuple[float, float]]] = defaultdict(list)
    for item in assessments:
        year, week, _ = item.date.isocalendar()
        week_key = year * 100 + week
        weekly_data[(week_key, item.subject)].append((item.percent, item.weight))

    rows: List[Dict[str, str]] = []
    previous_avg: Dict[str, float] = {}
    for (week, subject) in sorted(weekly_data.keys()):
        avg = weighted_average(weekly_data[(week, subject)])
        target = targets.get(subject, 75.0)
        delta = avg - previous_avg.get(subject, avg)
        progress_symbol = "↑" if delta > 0.5 else "↓" if delta < -0.5 else "→"

        if avg < target:
            gap = target - avg
            next_action = (
                f"Focus {weakest_types.get(subject, 'practice')} + 1 hr/day on key topics "
                f"(close {gap:.1f}% gap)"
            )
        else:
            next_action = "Maintain current strategy + 30 min revision"

        rows.append(
            {
                "Week": str(week),
                "Subject": subject,
                "Avg Marks": f"{avg:.1f}%",
                "Target": f"{target:.1f}%",
                "Progress": f"{progress_symbol} {delta:+.1f}%",
                "Next Action": next_action,
            }
        )
        previous_avg[subject] = avg

    return rows


def write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def maybe_create_charts(
    assessments: List[Assessment],
    averages: Dict[str, float],
    targets: Dict[str, float],
    outdir: Path,
) -> str:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        return "Charts skipped: matplotlib not installed."

    outdir.mkdir(parents=True, exist_ok=True)

    by_subject: Dict[str, List[Assessment]] = defaultdict(list)
    for item in assessments:
        by_subject[item.subject].append(item)

    plt.figure(figsize=(10, 5))
    for subject, items in by_subject.items():
        ordered = sorted(items, key=lambda x: x.date)
        plt.plot([x.date for x in ordered], [x.percent for x in ordered], marker="o", label=subject)
    plt.title("Marks Trend per Subject")
    plt.xlabel("Date")
    plt.ylabel("Score %")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "marks_trend.png")
    plt.close()

    subjects = sorted(averages.keys())
    avg_values = [averages[s] for s in subjects]
    target_values = [targets.get(s, 75.0) for s in subjects]

    x = range(len(subjects))
    plt.figure(figsize=(10, 5))
    plt.bar([i - 0.2 for i in x], avg_values, width=0.4, label="Average")
    plt.bar([i + 0.2 for i in x], target_values, width=0.4, label="Target")
    plt.xticks(list(x), subjects)
    plt.ylabel("Score %")
    plt.title("Average vs Target")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "avg_vs_target.png")
    plt.close()

    return "Charts generated: marks_trend.png, avg_vs_target.png"


def generate_summary(
    averages: Dict[str, float],
    targets: Dict[str, float],
    trends: Dict[str, str],
    weakest_types: Dict[str, str],
) -> str:
    rows: List[Tuple[str, float, float, str]] = []
    for subject, average in averages.items():
        target = targets.get(subject, 75.0)
        rows.append((subject, average, target, trends.get(subject, "steady")))

    weak = sorted(rows, key=lambda x: x[1] - x[2])
    strong = sorted(rows, key=lambda x: x[1] - x[2], reverse=True)

    lines = ["MARKS PERFORMANCE SUMMARY"]
    lines.append("\nSubject performance (avg vs target):")
    for subject, avg, target, trend in sorted(rows):
        lines.append(
            f"- {subject}: {avg:.1f}% vs target {target:.1f}% "
            f"({avg - target:+.1f}%), trend: {trend}"
        )

    lines.append("\nPriority focus subjects:")
    for subject, avg, target, _ in weak[:3]:
        lines.append(
            f"- {subject}: improve {weakest_types.get(subject, 'practice')} "
            f"(gap {target - avg:.1f}%)"
        )

    lines.append("\nStrongest subjects:")
    for subject, avg, target, _ in strong[:2]:
        lines.append(f"- {subject}: keep momentum ({avg - target:+.1f}% vs target)")

    lines.append("\nWeekly action formula: 5 sessions/week (1 hour each) for lowest-gap subjects.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Marks Performance MVP")
    parser.add_argument("--assessments", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, default=Path("marks_performance_mvp/output"))
    args = parser.parse_args()

    assessments = read_assessments(args.assessments)
    targets = read_targets(args.targets)

    averages = subject_averages(assessments)
    trends = subject_trends(assessments)
    weakest_types = weakest_assessment_types(assessments)

    summary = generate_summary(averages, targets, trends, weakest_types)
    tracker_rows = build_weekly_tracker(assessments, targets, weakest_types)

    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "summary.txt").write_text(summary + "\n", encoding="utf-8")
    write_csv(
        args.outdir / "weekly_tracker.csv",
        ["Week", "Subject", "Avg Marks", "Target", "Progress", "Next Action"],
        tracker_rows,
    )

    chart_message = maybe_create_charts(assessments, averages, targets, args.outdir)

    print(summary)
    print(f"\nWrote: {args.outdir / 'summary.txt'}")
    print(f"Wrote: {args.outdir / 'weekly_tracker.csv'}")
    print(chart_message)


if __name__ == "__main__":
    main()
