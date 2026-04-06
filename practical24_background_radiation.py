"""
================================================================================
Practical 24 — Natural Background Radiation in the Outdoor Field
Tri-Chandra Multiple Campus | Dept. of Physics | B.Sc. III Year | 2082

Location   : Rooftop, Tri-Chandra Multiple Campus, Kathmandu, Nepal
Instrument : Geiger-Müller (GM) Counter
Counting time per reading : 10 seconds

Objective
---------
To study the level of natural background radiation in the outdoor field
in all directions (east, west, north, south, up and down). Find the
standard error in all directions separately. Compile this database in a
single set and make a histogram showing Gaussian-like distribution.
Interpret the result.

Physics Background
------------------
Natural background radiation arises from:
  - Cosmic rays (high-energy particles from space)
  - Terrestrial radiation (radioactive decay in rocks/soil: U-238, Th-232, K-40)
  - Atmospheric radon (Rn-222 decay chain)

Since radioactive decay is a random process governed by quantum mechanics,
the number of counts N in a fixed time interval follows:

  - Poisson distribution  (exact, for rare random events)
  - Gaussian (Normal) distribution  (good approximation when mean > ~5)

For a Poisson process with mean µ:
    P(k) = (µ^k · e^(-µ)) / k!
    σ = √µ

The Gaussian approximation:
    P(x) = (1 / σ√2π) · exp(−(x−µ)² / 2σ²)

Statistical quantities
----------------------
  Standard Deviation : σ = √[ Σ(xᵢ − x̄)² / (N−1) ]
  Standard Error     : SE = σ / √N
  Probable Error     : PE = 0.6745 · σ

Author : Nabin Pandey | nabin.795401@trc.tu.edu.np
================================================================================
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import norm, poisson
import warnings
warnings.filterwarnings('ignore')

# ── 1. LOAD DATA ──────────────────────────────────────────────────────────────
df = pd.read_csv('data.csv')

# Fix: drop NaN (row 52 west column has missing value — data entry gap)
directions = ['down', 'up', 'north', 'east', 'south', 'west']

# ── 2. STATISTICS PER DIRECTION ───────────────────────────────────────────────
stats = {}
for d in directions:
    clean = df[d].dropna().values.astype(float)
    n    = len(clean)
    mean = clean.mean()
    std  = clean.std(ddof=1)          # sample std dev (Bessel corrected)
    se   = std / np.sqrt(n)           # standard error
    pe   = 0.6745 * std               # probable error (50% confidence)
    stats[d] = {
        'n': n, 'mean': mean, 'std': std,
        'se': se, 'pe': pe, 'data': clean
    }

# ── 3. COMBINED DATASET ───────────────────────────────────────────────────────
combined = np.concatenate([stats[d]['data'] for d in directions])
mu_c   = combined.mean()
std_c  = combined.std(ddof=1)
se_c   = std_c / np.sqrt(len(combined))
pe_c   = 0.6745 * std_c

# ── 4. PRINT RESULTS ──────────────────────────────────────────────────────────
print("=" * 70)
print("  PRACTICAL 24 — NATURAL BACKGROUND RADIATION")
print("  Location: Rooftop, Tri-Chandra Multiple Campus, Kathmandu")
print("  Counting time: 10 seconds per reading")
print("=" * 70)
print(f"\n  {'Direction':<10} {'n':>4}  {'Mean':>7}  {'Std Dev':>8}  "
      f"{'Std Error':>10}  {'Prob Error':>11}")
print("  " + "-" * 58)
for d in directions:
    s = stats[d]
    print(f"  {d.capitalize():<10} {s['n']:>4}  {s['mean']:>7.4f}  "
          f"{s['std']:>8.4f}  {s['se']:>10.4f}  {s['pe']:>11.4f}")
print("  " + "-" * 58)
print(f"  {'Combined':<10} {len(combined):>4}  {mu_c:>7.4f}  "
      f"{std_c:>8.4f}  {se_c:>10.4f}  {pe_c:>11.4f}")
print()
print(f"  Poisson check: mean = {mu_c:.4f}, variance = {std_c**2:.4f}")
print(f"  (For a Poisson process, mean ≈ variance — here ratio = {std_c**2/mu_c:.4f})")
print("=" * 70)

# ── 5. FIGURE ─────────────────────────────────────────────────────────────────
BG     = '#0d1117'; PANEL  = '#161b22'; BORDER = '#30363d'; GRID   = '#21262d'
BLUE   = '#58a6ff'; ORANGE = '#f0883e'; GREEN  = '#56d364'; PURPLE = '#bc8cff'
YELLOW = '#e3b341'; MUTED  = '#8b949e'; WHITE  = '#e6edf3'
COLORS = [BLUE, ORANGE, GREEN, PURPLE, YELLOW, '#ff7b72']

fig = plt.figure(figsize=(16, 11), facecolor=BG)
gs  = gridspec.GridSpec(3, 3, figure=fig,
                        hspace=0.52, wspace=0.38,
                        left=0.08, right=0.96, top=0.91, bottom=0.07)

def style_ax(ax, title=''):
    ax.set_facecolor(PANEL)
    for sp in ax.spines.values(): sp.set_edgecolor(BORDER)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.grid(True, color=GRID, linewidth=0.6, linestyle='--', alpha=0.8)
    if title:
        ax.set_title(title, color=WHITE, fontsize=10, fontweight='bold', pad=7)

# Panels 1–6: one histogram per direction
for i, d in enumerate(directions):
    row, col = divmod(i, 3)
    ax   = fig.add_subplot(gs[row, col])
    data = stats[d]['data']
    mu_d = stats[d]['mean']
    sd_d = stats[d]['std']

    bins = np.arange(data.min() - 0.5, data.max() + 1.5, 1)
    ax.hist(data, bins=bins, density=True, color=COLORS[i],
            alpha=0.55, edgecolor=BORDER, linewidth=0.6, label='Observed')

    # Gaussian fit
    x_g = np.linspace(data.min() - 1, data.max() + 1, 300)
    ax.plot(x_g, norm.pdf(x_g, mu_d, sd_d),
            color=WHITE, lw=1.8, label='Gaussian')

    # Poisson PMF overlay
    k_vals = np.arange(0, int(data.max()) + 2)
    ax.plot(k_vals, poisson.pmf(k_vals, mu_d), 'o--',
            color=YELLOW, markersize=3.5, lw=1.2, alpha=0.85, label='Poisson')

    ann = (f'μ = {mu_d:.2f}\n'
           f'σ = {sd_d:.2f}\n'
           f'SE = {stats[d]["se"]:.4f}\n'
           f'PE = {stats[d]["pe"]:.4f}')
    ax.text(0.97, 0.96, ann, transform=ax.transAxes,
            fontsize=7.8, va='top', ha='right',
            color=WHITE, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4',
                      facecolor='#21262d', edgecolor=COLORS[i], alpha=0.9))
    ax.set_xlabel('Counts per 10 s', fontsize=8.5)
    ax.set_ylabel('Probability Density', fontsize=8.5)
    style_ax(ax, f'{d.capitalize()} Direction')
    leg = ax.legend(fontsize=7.5, facecolor=PANEL, edgecolor=BORDER)
    for t in leg.get_texts(): t.set_color(WHITE)

# Panel 7 (bottom full-width): combined Gaussian histogram
ax7  = fig.add_subplot(gs[2, :])
bins_c = np.arange(combined.min() - 0.5, combined.max() + 1.5, 1)
ax7.hist(combined, bins=bins_c, density=True,
         color=BLUE, alpha=0.5, edgecolor=BORDER,
         linewidth=0.7, label=f'All directions combined (n={len(combined)})')

x_gc = np.linspace(combined.min() - 1, combined.max() + 1, 400)
ax7.plot(x_gc, norm.pdf(x_gc, mu_c, std_c),
         color=ORANGE, lw=2.3,
         label=f'Gaussian: μ={mu_c:.4f}, σ={std_c:.4f}')

k_c = np.arange(0, int(combined.max()) + 2)
ax7.plot(k_c, poisson.pmf(k_c, mu_c), 'o--',
         color=GREEN, markersize=4, lw=1.4, alpha=0.85,
         label=f'Poisson: λ={mu_c:.4f}')

ax7.axvline(mu_c, color=WHITE, lw=1.2, linestyle=':', alpha=0.7,
            label=f'Mean = {mu_c:.4f}')
ax7.axvspan(mu_c - std_c, mu_c + std_c, color=ORANGE, alpha=0.07,
            label='±1σ  (68.3% of data)')

ann7 = (f'μ = {mu_c:.4f}   σ = {std_c:.4f}\n'
        f'SE = {se_c:.4f}   PE = {pe_c:.4f}\n'
        f'n = {len(combined)}  (6 directions × ~100 readings each)')
ax7.text(0.98, 0.95, ann7, transform=ax7.transAxes,
         fontsize=9, va='top', ha='right',
         color=WHITE, fontfamily='monospace',
         bbox=dict(boxstyle='round,pad=0.5',
                   facecolor='#21262d', edgecolor=ORANGE, alpha=0.92))
ax7.set_xlabel('Counts per 10 s  (natural background radiation)', fontsize=10)
ax7.set_ylabel('Probability Density', fontsize=10)
style_ax(ax7, 'Combined Dataset — Gaussian-like Distribution of Natural Background Radiation')
leg7 = ax7.legend(fontsize=9, facecolor=PANEL, edgecolor=BORDER)
for t in leg7.get_texts(): t.set_color(WHITE)

fig.suptitle(
    'Practical 24 — Natural Background Radiation · Angular Distribution · '
    'GM Counter · Rooftop, Tri-Chandra Campus, Kathmandu',
    fontsize=12, fontweight='bold', color=WHITE, y=0.975)
fig.text(0.5, 0.003,
         'Tri-Chandra Multiple Campus · Department of Physics · B.Sc. III Year · 2082',
         ha='center', fontsize=8.5, color=MUTED)

plt.savefig('practical24_figure.png', dpi=180, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print("\n  Figure saved → practical24_figure.png")
