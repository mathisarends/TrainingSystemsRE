from training_system.features.plans.domain import Plan

PROGRESS_ROUNDING_STEP = 2.5


def progress_percent(plan: Plan) -> float:
    total_days = plan.block_length * len(plan.weekdays)
    if total_days <= 0:
        return 0.0
    position = plan.last_used_week_index * len(plan.weekdays) + plan.last_used_day_index
    raw_percent = (position / total_days) * 100
    return round(raw_percent / PROGRESS_ROUNDING_STEP) * PROGRESS_ROUNDING_STEP
