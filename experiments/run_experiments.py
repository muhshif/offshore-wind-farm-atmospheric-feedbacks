"""Run two small reproducible studies and export publication-style PNG/CSV outputs."""
import sys
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.wake_model import Turbine, aligned_grid, wind_field, farm_metrics

OUT = ROOT / 'figures'
RESULTS = ROOT / 'results'
OUT.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)
TURBINE = Turbine()


def main():
    # Experiment 1: wind field for 3 x 3 turbines, ambient 10 m/s, flow toward east.
    layout = aligned_grid(7, diameter=TURBINE.diameter)
    x = np.linspace(-500, layout[:, 0].max()+3200, 420)
    y = np.linspace(-1400, layout[:, 1].max()+1400, 270)
    xx, yy = np.meshgrid(x, y)
    field = wind_field(xx, yy, layout, 10., 0., TURBINE, 0.05)
    deficit_percent = 100*(1-field/10)
    fig, ax = plt.subplots(figsize=(10, 5.2), constrained_layout=True)
    c = ax.pcolormesh(xx/1000, yy/1000, deficit_percent, shading='auto',
                      cmap='viridis', vmin=0, vmax=45)
    ax.scatter(layout[:,0]/1000, layout[:,1]/1000, s=56, c='white',
               edgecolor='black', linewidth=.8, label='Hypothetical turbine')
    ax.set(xlabel='East / downwind distance (km)', ylabel='North distance (km)',
           title='Experiment 1 | Idealized offshore wind-farm hub-height wake')
    ax.set_aspect('equal', adjustable='box')
    fig.colorbar(c, ax=ax, label='Local wind-speed deficit (%)')
    ax.legend(loc='lower right')
    fig.savefig(OUT / '01_wind_speed_deficit.png', dpi=170)
    plt.close(fig)

    # Experiment 2: sensitivity to spacing and wake expansion k.
    spacing_values = np.arange(4., 12.1, 1.)
    k_values = [0.035, 0.05, 0.075]
    rows = []
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    for k in k_values:
        losses = []
        for spacing in spacing_values:
            metrics = farm_metrics(aligned_grid(spacing, diameter=TURBINE.diameter),
                                   k=k, turbine=TURBINE)
            loss = metrics['relative_power_loss_percent']
            losses.append(loss)
            rows.append({'spacing_D': spacing, 'wake_expansion_k': k,
                         **metrics})
        ax.plot(spacing_values, losses, marker='o', label=f'k = {k:.3f}')
    ax.set(xlabel='Turbine centre-to-centre spacing (rotor diameters)',
           ylabel='Illustrative relative power loss (%)',
           title='Experiment 2 | Spacing and wake-recovery sensitivity')
    ax.grid(True, alpha=.3)
    ax.legend(title='Wake expansion coefficient')
    fig.savefig(OUT / '02_spacing_sensitivity.png', dpi=170)
    plt.close(fig)

    # Supplemental: geometric effect of wind direction.
    directions = np.arange(-45, 46, 3)
    losses = [farm_metrics(layout, wind_direction_degrees=float(angle))['relative_power_loss_percent']
              for angle in directions]
    fig, ax = plt.subplots(figsize=(8.4, 5), constrained_layout=True)
    ax.plot(directions, losses, marker='.', markersize=5)
    ax.set(xlabel='Flow-to direction (degrees counterclockwise from east)',
           ylabel='Illustrative relative power loss (%)',
           title='Additional diagnostic | Wind-direction sensitivity')
    ax.grid(True, alpha=.3)
    fig.savefig(OUT / '03_wind_direction.png', dpi=170)
    plt.close(fig)

    with (RESULTS / 'spacing_sensitivity.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    baseline = farm_metrics(layout, k=.05)
    print('Baseline: 3 x 3 layout, 7D spacing, U0=10 m/s, Ct=0.8, k=0.05')
    print(f"Illustrative relative power loss: {baseline['relative_power_loss_percent']:.2f}%")
    print('Generated 3 PNG figures and results/spacing_sensitivity.csv')


if __name__ == '__main__':
    main()
