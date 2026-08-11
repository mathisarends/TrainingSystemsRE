from uuid import UUID

from training_system.features.plans.domain import Plan


def compute_weight_recommendations(plan: Plan) -> dict[UUID, float]:
    """Maps entry id -> previous week's weight, for entries whose exercise
    name and rep count match the same position in the previous week. The
    first week never has recommendations."""
    recommendations: dict[UUID, float] = {}
    for week_index in range(1, len(plan.weeks)):
        week = plan.weeks[week_index]
        previous_week = plan.weeks[week_index - 1]
        for day_index, day in enumerate(week.days):
            if day_index >= len(previous_week.days):
                continue
            previous_day = previous_week.days[day_index]
            for position, entry in enumerate(day.entries):
                if position >= len(previous_day.entries):
                    continue
                previous_entry = previous_day.entries[position]
                if (
                    previous_entry.exercise_name == entry.exercise_name
                    and previous_entry.reps == entry.reps
                    and previous_entry.weight is not None
                ):
                    recommendations[entry.id] = previous_entry.weight
    return recommendations
