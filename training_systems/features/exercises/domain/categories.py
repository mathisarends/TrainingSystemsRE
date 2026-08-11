"""The fixed set of selectable exercise categories and their default catalog.

Transcribed from Features.md's default-catalog table (the internal
"- Bitte Auswählen -" placeholder is intentionally excluded).
"""

from training_systems.features.exercises.domain.entities import (
    CategoryDefaults,
    ExerciseCategory,
)

AVAILABLE_CATEGORIES: tuple[ExerciseCategory, ...] = tuple(ExerciseCategory)

DEFAULT_CATEGORY_DEFAULTS: tuple[CategoryDefaults, ...] = (
    CategoryDefaults(ExerciseCategory.SQUAT, 240, 3, 7, 7.5),
    CategoryDefaults(ExerciseCategory.BENCH, 180, 4, 8, 8.0),
    CategoryDefaults(ExerciseCategory.DEADLIFT, 240, 3, 6, 7.0),
    CategoryDefaults(ExerciseCategory.OVERHEADPRESS, 150, 3, 10, 8.5),
    CategoryDefaults(ExerciseCategory.CHEST, 120, 3, 12, 8.5),
    CategoryDefaults(ExerciseCategory.BACK, 120, 3, 12, 8.5),
    CategoryDefaults(ExerciseCategory.SHOULDER, 90, 3, 12, 8.5),
    CategoryDefaults(ExerciseCategory.TRICEPS, 90, 3, 12, 8.5),
    CategoryDefaults(ExerciseCategory.BICEPS, 90, 3, 12, 8.5),
    CategoryDefaults(ExerciseCategory.LEGS, 120, 3, 12, 8.5),
)

ExerciseName = str
MaxFactor = float | None
DefaultExercise = tuple[ExerciseCategory, ExerciseName, MaxFactor]

DEFAULT_EXERCISES: tuple[DefaultExercise, ...] = (
    (ExerciseCategory.SQUAT, "Lowbar - Squat", None),
    (ExerciseCategory.SQUAT, "Highbar - Squat", None),
    (ExerciseCategory.SQUAT, "Paused Squat", 0.875),
    (ExerciseCategory.SQUAT, "Tempo Squat (3:1:0)", 0.875),
    (ExerciseCategory.SQUAT, "Hack-Squat", 1.5),
    (ExerciseCategory.SQUAT, "Bulgurian Split Squats", 0.0),
    (ExerciseCategory.SQUAT, "Legpress", 2.0),
    (ExerciseCategory.BENCH, "Comp. Bench", None),
    (ExerciseCategory.BENCH, "Larsen Press", 0.95),
    (ExerciseCategory.BENCH, "Close Grip Bench", 0.95),
    (ExerciseCategory.BENCH, "Spoto Bench", None),
    (ExerciseCategory.BENCH, "Tempo Bench", 0.95),
    (ExerciseCategory.BENCH, "3ct Pause Bench", 0.95),
    (ExerciseCategory.BENCH, "Chestpress", 1.1),
    (ExerciseCategory.BENCH, "Incline Press", 1.1),
    (ExerciseCategory.DEADLIFT, "Conventional", None),
    (ExerciseCategory.DEADLIFT, "Sumo", None),
    (ExerciseCategory.DEADLIFT, "Paused Deadlift", 0.9),
    (ExerciseCategory.DEADLIFT, "Deficit Deadlift", 0.9),
    (ExerciseCategory.DEADLIFT, "RDLs", 0.825),
    (ExerciseCategory.DEADLIFT, "B-Stance RDLs", 0.0),
    (ExerciseCategory.DEADLIFT, "Stiff-Leg DL", 0.825),
    (ExerciseCategory.OVERHEADPRESS, "Overheadpress", None),
    (ExerciseCategory.OVERHEADPRESS, "Push-Press", None),
    (ExerciseCategory.OVERHEADPRESS, "Dumbell Overheadpress", None),
    (ExerciseCategory.OVERHEADPRESS, "Shoulderpress", None),
    (ExerciseCategory.CHEST, "Dips", None),
    (ExerciseCategory.CHEST, "Butterfly", None),
    (ExerciseCategory.CHEST, "Deficit Pushups", None),
    (ExerciseCategory.BACK, "Pull-Up", None),
    (ExerciseCategory.BACK, "Dumbell Row", None),
    (ExerciseCategory.BACK, "Pulldowns (wide-grip)", None),
    (ExerciseCategory.BACK, "Pulldowns (close-grip)", None),
    (ExerciseCategory.BACK, "T-Bar Row", None),
    (ExerciseCategory.BACK, "Chestsupported Row", None),
    (ExerciseCategory.SHOULDER, "Reverse Flyes", None),
    (ExerciseCategory.SHOULDER, "Lateral Raise", None),
    (ExerciseCategory.SHOULDER, "Facepulls", None),
    (ExerciseCategory.SHOULDER, "Upright Rows", None),
    (ExerciseCategory.SHOULDER, "Front-Raises", None),
    (ExerciseCategory.TRICEPS, "Triceps-Extensions", None),
    (ExerciseCategory.TRICEPS, "French-Press Flat", None),
    (ExerciseCategory.TRICEPS, "Cable-Pushdowns", None),
    (ExerciseCategory.TRICEPS, "Diamond Pushups", None),
    (ExerciseCategory.BICEPS, "Biceps-Curls", None),
    (ExerciseCategory.BICEPS, "Cable Curls", None),
    (ExerciseCategory.BICEPS, "Hammer Curls", None),
    (ExerciseCategory.LEGS, "Hip Thrusts", None),
    (ExerciseCategory.LEGS, "Hyperextensions", None),
    (ExerciseCategory.LEGS, "Leg Extension", None),
    (ExerciseCategory.LEGS, "Leg Curl", None),
    (ExerciseCategory.LEGS, "Calf Raises", None),
    (ExerciseCategory.LEGS, "Hip Adduction", None),
    (ExerciseCategory.LEGS, "Hip Abduction", None),
)
