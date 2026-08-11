import pytest

from training_system.features.plans.domain.values import (
    deload_target_rpe_for,
    rpe_cap_for,
)


@pytest.mark.parametrize("category", ["Squat", "Bench", "Deadlift"])
def test_rpe_cap_is_nine_for_main_lifts(category: str) -> None:
    assert rpe_cap_for(category) == 9.0


@pytest.mark.parametrize("category", ["Overheadpress", "Chest", "Legs"])
def test_rpe_cap_is_ten_for_accessory_categories(category: str) -> None:
    assert rpe_cap_for(category) == 10.0


@pytest.mark.parametrize("category", ["Squat", "Bench", "Deadlift"])
def test_deload_target_rpe_is_six_for_main_lifts(category: str) -> None:
    assert deload_target_rpe_for(category) == 6.0


@pytest.mark.parametrize("category", ["Overheadpress", "Chest", "Legs"])
def test_deload_target_rpe_is_seven_for_accessory_categories(category: str) -> None:
    assert deload_target_rpe_for(category) == 7.0
