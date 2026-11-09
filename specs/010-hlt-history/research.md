# Research: HLT history

**R1. Which rows.** HEALTH_METRIC_RECORD of the mother and metric, `measured_at` inside From – To inclusive, newest first in the list and oldest first on the chart. Fetal heart rate: source "From visit" only (BR-005).

**R2. Labels.** Group 2: `thresholds.evaluate` with the row's own `glucose_context`. Group 1 and fetal heart rate: no label (BR-003, BR-005). Every row shows its source (BR-004).

**R3. Lines.** Blood pressure: both values of the rule rows, drawn at systolic and diastolic. Blood glucose: the rule of the selected context only. Urine protein: the rule's level on the scale. Fetal heart rate: the two ends of the "Display only" row, as reference lines, not a threshold. Group 1: none. All read from THRESHOLD_RULE.

**R4. Chart.** Inline SVG, viewBox 320 × 160 as in the UI package. `x` by time, `y` scaled to the data and the lines with a small margin. One point: a dot, no line. No chart library.

**R5. S-027 cards.** WATCH_FLAG joined with STAFF for the doctor's name; the latest METRIC_REPORT of that metric joined with its record for the value, time and label ("none yet" otherwise).
