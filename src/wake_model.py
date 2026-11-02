"""Transparent idealized Jensen (Park) top-hat wind-farm wake model.

A teaching-scale engineering model, not a mesoscale atmospheric simulation.
Distances are metres and wind speeds are m/s. Mathematical assumptions in README.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Turbine:
    diameter: float = 180.0       # m, hypothetical machine
    thrust_coefficient: float = 0.8  # dimensionless, held constant
    rated_power_mw: float = 10.0   # hypothetical; power curve is illustrative


def wake_deficit(dx, dy, rotor_diameter=180., ct=0.8, k=0.05):
    """Fractional speed deficit for a point inside a Jensen top-hat wake.

    dx/dy are streamwise/crosswind displacements relative to turbine.
    The deficit is zero upstream and outside the expanding wake radius.
    """
    if not (rotor_diameter > 0 and 0 <= ct < 1 and k > 0):
        raise ValueError('Require diameter>0, 0<=ct<1, wake expansion k>0')
    dx, dy = np.broadcast_arrays(np.asarray(dx, float), np.asarray(dy, float))
    safe_x = np.maximum(dx, 0.0)
    radius = rotor_diameter / 2.0 + k * safe_x
    frac = (1. - np.sqrt(1. - ct)) / (1. + 2. * k * safe_x / rotor_diameter)**2
    return np.where((dx > 0.0) & (np.abs(dy) <= radius), frac, 0.)


def rotate_to_wind(points, wind_direction_degrees):
    """Rotate (east,north) map coordinates into wind-aligned (downwind,crosswind).

    Direction is the direction the flow GOES TO, degrees CCW from east.
    Thus 0 -> wind travels east, 90 -> north. NOT meteorological 'from'.
    """
    points = np.asarray(points, float)
    angle = np.deg2rad(wind_direction_degrees)
    along = points[..., 0] * np.cos(angle) + points[..., 1] * np.sin(angle)
    cross = -points[..., 0] * np.sin(angle) + points[..., 1] * np.cos(angle)
    return np.stack([along, cross], axis=-1)


def circular_overlap_fraction(radius_wake, radius_rotor, separation):
    """Wake-circle overlap as fraction of the downstream turbine rotor area."""
    r1 = float(radius_wake)
    r2 = float(radius_rotor)
    d = float(abs(separation))
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return min(r1, r2)**2 / r2**2
    a1 = np.arccos(np.clip((d*d+r1*r1-r2*r2)/(2*d*r1), -1., 1.))
    a2 = np.arccos(np.clip((d*d+r2*r2-r1*r1)/(2*d*r2), -1., 1.))
    radicand = max(0., (-d+r1+r2)*(d+r1-r2)*(d-r1+r2)*(d+r1+r2))
    area = r1*r1*a1 + r2*r2*a2 - 0.5*np.sqrt(radicand)
    return float(np.clip(area/(np.pi*r2*r2), 0., 1.))


def turbine_wind_speeds(layout, ambient_speed=10., wind_direction_degrees=0.,
                        turbine=Turbine(), k=0.05):
    """Approximate turbine inflows via Jensen wake deficits, quadratic combination.

    For each downstream turbine, use geometric overlap of each upstream top-hat
    wake with its rotor disk. Jensen assumes steady unidirectional uniform inflow.
    """
    if ambient_speed <= 0:
        raise ValueError('Ambient speed must be positive')
    coords = rotate_to_wind(layout, wind_direction_degrees)
    speeds = np.full(len(coords), ambient_speed, dtype=float)
    for j in range(len(coords)):
        dsq = 0.
        for i in range(len(coords)):
            dx = coords[j, 0] - coords[i, 0]
            if dx <= 0:
                continue
            dy = coords[j, 1] - coords[i, 1]
            r_wake = turbine.diameter/2 + k*dx
            overlap = circular_overlap_fraction(r_wake, turbine.diameter/2, dy)
            deficit = (1-np.sqrt(1-turbine.thrust_coefficient)) / (1+2*k*dx/turbine.diameter)**2
            dsq += (deficit * overlap)**2
        speeds[j] = ambient_speed * (1 - min(np.sqrt(dsq), 0.999))
    return speeds


def wind_field(x, y, layout, ambient_speed=10., wind_direction_degrees=0.,
               turbine=Turbine(), k=0.05):
    """Two-dimensional hub-height visualization; wind speed at grid points."""
    if ambient_speed <= 0:
        raise ValueError('Ambient speed must be positive')
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    grid = rotate_to_wind(np.stack([x, y], axis=-1), wind_direction_degrees)
    source = rotate_to_wind(layout, wind_direction_degrees)
    deficit_sq = np.zeros_like(x)
    for sx, sy in source:
        deficit_sq += wake_deficit(grid[...,0]-sx, grid[...,1]-sy,
                                  turbine.diameter, turbine.thrust_coefficient, k)**2
    return ambient_speed * (1 - np.minimum(np.sqrt(deficit_sq), .999))


def illustrative_power_mw(speeds, turbine=Turbine()):
    """Generic educational power curve; NOT any manufacturer's power curve.

    Zero below 3 m/s, cubic rise 3--12 m/s, constant rated power 12--25 m/s,
    zero at/above 25 m/s. Not a calibrated physical power prediction.
    """
    u = np.asarray(speeds, float)
    p = np.zeros_like(u)
    mask = (u >= 3) & (u < 12)
    p[mask] = turbine.rated_power_mw * (u[mask]**3-3**3) / (12**3-3**3)
    p[(u >= 12) & (u < 25)] = turbine.rated_power_mw
    return p


def aligned_grid(spacing_d=7., n_rows=3, n_cols=3, diameter=180.):
    """3x3 hypothetical grid: columns are in wind's downwind (east) direction."""
    spacing = spacing_d * diameter
    return np.array([(i*spacing, j*spacing) for i in range(n_cols)
                     for j in range(n_rows)], dtype=float)


def farm_metrics(layout, wind_direction_degrees=0., k=.05,
                 ambient_speed=10., turbine=Turbine()):
    speeds = turbine_wind_speeds(layout, ambient_speed, wind_direction_degrees,
                                turbine, k)
    power = illustrative_power_mw(speeds, turbine)
    free_power = float(illustrative_power_mw(np.asarray([ambient_speed]), turbine)[0]) * len(layout)
    return {
        'mean_turbine_speed_ms': float(speeds.mean()),
        'total_power_mw': float(power.sum()),
        'free_stream_power_mw': free_power,
        'relative_power_loss_percent': float(100 * (1 - power.sum() / free_power)) if free_power > 0 else float('nan'),
    }
