# Research: TML journey

**R1. Stages.** `STAGES` holds the D-75 boundaries in one place. The default is the stage of the current week. A stage starting after the current week is "not reached": no content, export disabled. Weeks after the current week are never listed.

**R2. Week blocks.** `weeks.week_content` (the builder of S-048) gives the visits, diary and messages of a week; weeks without any of them are left out. All photos of a diary entry come from DIARY_IMAGE by `sort_order`.

**R3. Counts.** Visits, diary entries and photos of the selected stage. The list of stages shows each stage's visit count and whether it is past, current or to come.

**R4. Album.** A separate page without the app frame, with print CSS; `window.print()` runs when it opens with `?print=1`. Only GET queries; `total_changes` does not move (BR-007). With no content the route redirects to S-105.
