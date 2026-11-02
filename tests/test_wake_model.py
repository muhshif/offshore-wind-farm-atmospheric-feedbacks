import numpy as np
import pytest
from src.wake_model import (wake_deficit, aligned_grid, turbine_wind_speeds,
                            farm_metrics, rotate_to_wind, circular_overlap_fraction)


def test_no_upstream_wake():
    assert wake_deficit(-200., 0.) == 0
    assert wake_deficit(0., 0.) == 0


def test_wake_decays_downstream():
    assert 0 < wake_deficit(1800., 0.) < wake_deficit(360., 0.) < 1


def test_outside_wake():
    assert wake_deficit(200., 2000.) == 0


def test_rotor_overlap():
    assert circular_overlap_fraction(150., 90., 0.) == pytest.approx(1)
    assert circular_overlap_fraction(90., 90., 200.) == 0.
    assert circular_overlap_fraction(90., 90., 90.) > 0


def test_isolated_turbine_undisturbed():
    assert turbine_wind_speeds(np.array([[0., 0.]]))[0] == pytest.approx(10)


def test_downwind_turbine_has_lower_speed():
    values = turbine_wind_speeds(np.array([[0., 0.], [1260., 0.]]))
    assert values[0] == pytest.approx(10)
    assert 0 < values[1] < values[0]


def test_more_spacing_reduces_aligned_wake_losses():
    close = farm_metrics(aligned_grid(5))['relative_power_loss_percent']
    far = farm_metrics(aligned_grid(10))['relative_power_loss_percent']
    assert close > far > 0


def test_wind_direction_definition():
    assert rotate_to_wind([[0, 100]], 90)[0, 0] == pytest.approx(100)


def test_invalid_parameters_raise():
    with pytest.raises(ValueError):
        wake_deficit(100., 0., ct=1.1)
