"""
Visualization for Hobbes Leviathan CA experiments.

Generates publication-quality figures covering all three levels of analysis:
  Level 1 — Emergence: cooperation time series
  Level 2 — Expansion: cluster growth, interface dynamics
  Level 3 — Stabilization: final state distributions, phase diagrams

Uses matplotlib + seaborn for consistent, clean styling.
"""

import numpy as np
import json
import os
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import seaborn as sns

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'legend.fontsize': 8,
    'figure.titlesize': 13,
})

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
SNAPSHOT_TIMES = [0, 250, 500, 600, 750, 1000]
LEVIATHAN_TIME = 500
TOTAL_STEPS = 1000

# Color scheme
COLOR_C = '#2ecc71'      # Cooperator green
COLOR_D = '#e74c3c'      # Defector red
COLOR_LEVIATHAN = '#8e44ad'  # Leviathan purple
COLOR_NO_LEVIATHAN = '#3498db'  # No Leviathan blue
B_COLORS = {1.2: '#1a5276', 1.4: '#2980b9', 1.6: '#7fb3d8',
            1.8: '#e67e22', 2.0: '#c0392b'}
P_STYLES = {0.1: ('dashed', 1.0), 0.3: ('dashdot', 1.5), 0.5: ('solid', 2.0)}

# Grid colormap: yellow=cooperator, dark=defector
GRID_CMAP = LinearSegmentedColormap.from_list('hobbes', ['#2c3e50', '#f1c40f'])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_data():
    """Load summary and metadata from disk."""
    with open(os.path.join(OUTPUT_DIR, 'summary.json'), 'r') as f:
        summary = json.load(f)
    with open(os.path.join(OUTPUT_DIR, 'metadata.json'), 'r') as f:
        meta = json.load(f)
    # Convert string keys back
    return summary, meta


def _parse_summary(summary):
    """Convert JSON summary back to usable numeric-keyed dicts."""
    parsed = {'A': {}, 'B': {}}
    for b_str, v in summary['A'].items():
        parsed['A'][float(b_str)] = v
    for b_str, p_dict in summary['B'].items():
        parsed['B'][float(b_str)] = {}
        for p_str, v in p_dict.items():
            parsed['B'][float(b_str)][float(p_str)] = v
    return parsed


# --------------------------------------------------------------------------
# Figure 1: Time series of f_c(t) — Condition A (Level 1)
# --------------------------------------------------------------------------

def fig1_condition_a_timeseries(summary):
    """Cooperation fraction over time for all b values (no Leviathan)."""
    fig, ax = plt.subplots(figsize=(8, 4.5))

    data_a = summary['A']
    for b in sorted(data_a.keys()):
        d = data_a[b]
        label = f'b = {b:.1f}'
        ax.plot(d['time'], d['f_c_mean'], color=B_COLORS[b],
                linewidth=1.5, label=label, alpha=0.9)

    ax.axhline(y=0.5, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.set_xlabel('Time step $t$')
    ax.set_ylabel('Cooperation fraction $f_c(t)$')
    ax.set_title('Cooperation Dynamics — State of Nature (No Leviathan)')
    ax.set_ylim(-0.02, 1.02)
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
              title='Temptation $b$', frameon=True, fancybox=True)
    ax.grid(True, alpha=0.3)

    sns.despine()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_condition_a_timeseries.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_condition_a_timeseries.pdf'))
    plt.close(fig)
    print("  Figure 1 saved.")


# --------------------------------------------------------------------------
# Figure 2: Time series comparing A vs B (b=1.6, all p) — core finding
# --------------------------------------------------------------------------

def fig2_ab_comparison(summary):
    """
    Central comparison: f_c(t) for Condition A vs Condition B at b=1.6
    (the critical phase transition region) across all p values.
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), sharex=True, sharey=True)

    b_focus = 1.6  # Critical region
    data_a = summary['A'][b_focus]
    data_b = summary['B'][b_focus]

    for idx, p in enumerate(sorted(data_b.keys())):
        ax = axes[idx]
        d_b = data_b[p]

        # Condition A (baseline, same for all subplots)
        ax.plot(data_a['time'], data_a['f_c_mean'], color=COLOR_NO_LEVIATHAN,
                linewidth=1.8, label='No Leviathan (A)', alpha=0.7, linestyle='--')
        ax.fill_between(data_a['time'],
                        np.array(data_a['f_c_mean']) - np.array(data_a['f_c_std']),
                        np.array(data_a['f_c_mean']) + np.array(data_a['f_c_std']),
                        color=COLOR_NO_LEVIATHAN, alpha=0.08)

        # Condition B
        ax.plot(d_b['time'], d_b['f_c_mean'], color=COLOR_LEVIATHAN,
                linewidth=1.8, label=f'Leviathan (B, p={p:.1f})')
        ax.fill_between(d_b['time'],
                        np.array(d_b['f_c_mean']) - np.array(d_b['f_c_std']),
                        np.array(d_b['f_c_mean']) + np.array(d_b['f_c_std']),
                        color=COLOR_LEVIATHAN, alpha=0.08)

        # Leviathan introduction line
        ax.axvline(x=LEVIATHAN_TIME, color=COLOR_LEVIATHAN, linestyle=':',
                   linewidth=1.2, alpha=0.6, label='Leviathan introduced')
        ax.set_title(f'$p = {p:.1f}$')
        ax.set_xlabel('Time step $t$')
        if idx == 0:
            ax.set_ylabel('Cooperation fraction $f_c(t)$')
        ax.set_ylim(-0.02, 1.02)
        ax.legend(fontsize=7, loc='lower right')
        ax.grid(True, alpha=0.3)

    fig.suptitle(f'Leviathan Effect at $b = {b_focus:.1f}$ (Critical Region)',
                 fontweight='bold', y=1.01)
    sns.despine()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig2_ab_comparison.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig2_ab_comparison.pdf'))
    plt.close(fig)
    print("  Figure 2 saved.")


# --------------------------------------------------------------------------
# Figure 3: Full b-p grid comparison (Level 3 — Stabilization)
# --------------------------------------------------------------------------

def fig3_full_grid(summary):
    """
    5×3 grid: rows=b, columns=p. Each subplot shows A vs B time series.
    This is the comprehensive visualization.
    """
    b_vals = sorted(summary['A'].keys())
    p_vals = sorted(summary['B'][b_vals[0]].keys())

    fig, axes = plt.subplots(len(b_vals), len(p_vals),
                             figsize=(14, 12), sharex=True, sharey=True)

    for i, b in enumerate(b_vals):
        data_a = summary['A'][b]
        data_b_set = summary['B'][b]
        for j, p in enumerate(p_vals):
            ax = axes[i, j]
            d_b = data_b_set[p]

            # Condition A
            ax.plot(data_a['time'], data_a['f_c_mean'],
                    color=COLOR_NO_LEVIATHAN, linewidth=1.2, alpha=0.6,
                    linestyle='--')
            # Condition B
            ax.plot(d_b['time'], d_b['f_c_mean'],
                    color=COLOR_LEVIATHAN, linewidth=1.5)

            ax.axvline(x=LEVIATHAN_TIME, color=COLOR_LEVIATHAN,
                       linestyle=':', linewidth=0.8, alpha=0.5)
            ax.set_ylim(-0.02, 1.02)

            # Row/col labels
            if j == 0:
                ax.set_ylabel(f'$b={b:.1f}$\n$f_c$', fontsize=9)
            if i == 0:
                ax.set_title(f'$p={p:.1f}$', fontsize=11)
            if i == len(b_vals) - 1:
                ax.set_xlabel('$t$', fontsize=9)

            ax.grid(True, alpha=0.2)

    # Legend
    custom_lines = [
        Line2D([0], [0], color=COLOR_NO_LEVIATHAN, linestyle='--', linewidth=1.5, label='No Leviathan (A)'),
        Line2D([0], [0], color=COLOR_LEVIATHAN, linestyle='-', linewidth=1.5, label='With Leviathan (B)'),
    ]
    fig.legend(handles=custom_lines, loc='lower center', ncol=2,
               bbox_to_anchor=(0.5, -0.02), fontsize=10, frameon=True)

    fig.suptitle('Figure 3: Cooperation Dynamics — Full Parameter Grid',
                 fontweight='bold', y=1.01)
    sns.despine()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_full_grid.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_full_grid.pdf'))
    plt.close(fig)
    print("  Figure 3 saved.")


# --------------------------------------------------------------------------
# Figure 4: Spatial snapshots
# --------------------------------------------------------------------------

def fig4_spatial_snapshots():
    """Grid snapshots at key time points for Condition A and B."""
    snap_file = os.path.join(OUTPUT_DIR, 'snapshots.npz')
    if not os.path.exists(snap_file):
        print("  [Skip] Snapshots file not found. Run run_experiments.py first.")
        return

    snap = np.load(snap_file, allow_pickle=True)
    b_vals = [1.2, 1.4, 1.6, 1.8, 2.0]
    p_display = [0.1, 0.3, 0.5]  # Three p values for display

    # Find matching keys
    # Build a dict: (cond, b, p, t) -> grid
    available = {}
    for key in snap.keys():
        parts = key.split('_')
        # Format: A_b1.2_pNA_t0 or B_b1.6_p0.3_t750 etc.
        cond = parts[0]
        b = float(parts[1][1:])
        p_str = parts[2][1:]  # 'NA' or '0.1' etc.
        p = None if p_str == 'NA' else float(p_str)
        t = int(parts[3][1:])
        available[(cond, b, p, t)] = snap[key]

    # Figure 4a: Condition A snapshots (5 b values × 6 time points)
    fig, axes = plt.subplots(len(b_vals), len(SNAPSHOT_TIMES),
                             figsize=(14, 11))

    for i, b in enumerate(b_vals):
        for j, t in enumerate(SNAPSHOT_TIMES):
            ax = axes[i, j]
            grid = available.get(('A', b, None, t))
            if grid is not None:
                ax.imshow(grid, cmap=GRID_CMAP, interpolation='none',
                          vmin=0, vmax=1)
            ax.set_xticks([])
            ax.set_yticks([])
            if j == 0:
                ax.set_ylabel(f'$b={b:.1f}$', fontsize=10, rotation=0,
                              labelpad=20, ha='right')
            if i == 0:
                label = f'$t={t}$'
                if t == LEVIATHAN_TIME:
                    label += '\n(Leviathan)'
                ax.set_title(label, fontsize=9)
            # Thin border
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(0.3)

    fig.suptitle('Spatial Snapshots — State of Nature (No Leviathan)',
                 fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4a_spatial_snapshots_a.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4a_spatial_snapshots_a.pdf'))
    plt.close(fig)
    print("  Figure 4a saved.")

    # Figure 4b: Condition B snapshots (3 b × 6 time × 3 p → focus on b=1.6)
    fig, axes = plt.subplots(len(p_display), len(SNAPSHOT_TIMES),
                             figsize=(14, 6.5))
    b_show = 1.6

    for i, p in enumerate(p_display):
        for j, t in enumerate(SNAPSHOT_TIMES):
            ax = axes[i, j]
            grid = available.get(('B', b_show, p, t))
            if grid is not None:
                ax.imshow(grid, cmap=GRID_CMAP, interpolation='none',
                          vmin=0, vmax=1)
            ax.set_xticks([])
            ax.set_yticks([])
            if j == 0:
                ax.set_ylabel(f'$p={p:.1f}$', fontsize=10, rotation=0,
                              labelpad=20, ha='right')
            if i == 0:
                label = f'$t={t}$'
                if t == LEVIATHAN_TIME:
                    label += '\n(Leviathan)'
                ax.set_title(label, fontsize=9)
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(0.3)

    fig.suptitle(f'Figure 4b: Spatial Snapshots — Leviathan at $t=500$, $b={b_show}$',
                 fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4b_spatial_snapshots_b.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4b_spatial_snapshots_b.pdf'))
    plt.close(fig)
    print("  Figure 4b saved.")


# --------------------------------------------------------------------------
# Figure 5: Final state analysis (Level 3 — Stabilization)
# --------------------------------------------------------------------------

def fig5_final_state(summary):
    """Bar chart: final cooperation fraction f_c^∞ for all conditions."""
    data_a = summary['A']
    data_b = summary['B']
    b_vals = sorted(data_a.keys())
    p_vals = sorted(data_b[b_vals[0]].keys())

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(b_vals))
    width = 0.2

    # Condition A bars
    final_a = []
    for b in b_vals:
        # Last 500 steps average
        f_mean = np.array(data_a[b]['f_c_mean'])
        final_a.append(np.mean(f_mean[-500:]))
    ax.bar(x - width * 1.5, final_a, width, color=COLOR_NO_LEVIATHAN,
           alpha=0.7, label='No Leviathan (A)')

    # Condition B bars (grouped by p)
    for pi, p in enumerate(p_vals):
        final_b = []
        for b in b_vals:
            f_mean = np.array(data_b[b][p]['f_c_mean'])
            final_b.append(np.mean(f_mean[-500:]))
        ax.bar(x + width * (pi - 0.5), final_b, width,
               color=plt.cm.Purples(0.4 + 0.2 * (pi + 1)),
               alpha=0.85, label=f'Leviathan $p={p:.1f}$')

    ax.set_xticks(x)
    ax.set_xticklabels([f'$b={b:.1f}$' for b in b_vals])
    ax.set_ylabel('Final cooperation fraction $f_c^{{\\infty}}$')
    ax.set_title('Final Cooperation Level by Temptation and Penalty')
    ax.set_ylim(0, 1.05)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, alpha=0.3, axis='y')

    sns.despine()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig5_final_state.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig5_final_state.pdf'))
    plt.close(fig)
    print("  Figure 5 saved.")


# --------------------------------------------------------------------------
# Figure 6: Leviathan trajectory change (Δf_c after introduction)
# --------------------------------------------------------------------------

def fig6_trajectory_change(summary):
    """
    Show the CHANGE in cooperation trajectory after Leviathan introduction.
    Δf_c(t) = f_c^B(t) - f_c^A(t) for t > 500.
    """
    data_a = summary['A']
    data_b = summary['B']
    b_vals = sorted(data_a.keys())
    p_vals = sorted(data_b[b_vals[0]].keys())

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    for pi, p in enumerate(p_vals):
        ax = axes[pi]
        for b in b_vals:
            f_a = np.array(data_a[b]['f_c_mean'])
            f_b = np.array(data_b[b][p]['f_c_mean'])
            delta = f_b - f_a

            time = data_a[b]['time']
            # Show from t=450 (before Leviathan) to end
            mask = np.array(time) >= 450
            ax.plot(np.array(time)[mask], delta[mask],
                    color=B_COLORS[b], linewidth=1.5,
                    label=f'$b={b:.1f}$')

        ax.axvline(x=LEVIATHAN_TIME, color=COLOR_LEVIATHAN,
                   linestyle=':', linewidth=1.2, alpha=0.6)
        ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.8, alpha=0.5)
        ax.set_title(f'$p = {p:.1f}$')
        ax.set_xlabel('Time step $t$')
        ax.set_ylabel('$\\Delta f_c = f_c^B - f_c^A$')
        ax.legend(fontsize=7, loc='upper left')
        ax.grid(True, alpha=0.3)

    # Hide unused subplots (3 p values → use first 3 of 6)
    for pi in range(len(p_vals), 6):
        axes[pi].set_visible(False)

    fig.suptitle('Figure 6: Leviathan Trajectory Change ($\\Delta f_c$) by Penalty Strength',
                 fontweight='bold', y=1.01)
    sns.despine()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig6_trajectory_change.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig6_trajectory_change.pdf'))
    plt.close(fig)
    print("  Figure 6 saved.")


# --------------------------------------------------------------------------
# Figure 7: Phase diagram (Level 3 — steady-state classification)
# --------------------------------------------------------------------------

def fig7_phase_diagram(summary):
    """Phase diagram: final state type in (b, p) space."""
    data_a = summary['A']
    data_b = summary['B']
    b_vals = sorted(data_a.keys())
    p_vals = sorted(data_b[b_vals[0]].keys())

    # Classify final states
    def classify(f_c_final, a_max_final):
        if f_c_final > 0.85:
            return 3  # Cooperation dominant
        elif f_c_final < 0.05:
            return 0  # Defection dominant
        elif a_max_final > 0.3:
            return 2  # Clustered coexistence
        else:
            return 1  # Fragmented coexistence

    # Build matrix: rows=b, cols=p
    matrix = np.zeros((len(b_vals), len(p_vals)))
    matrix_a = np.zeros((len(b_vals), 1))

    for i, b in enumerate(b_vals):
        f_a = np.mean(np.array(data_a[b]['f_c_mean'])[-500:])
        a_a = np.mean(np.array(data_a[b]['a_max_mean'])[-500:])
        matrix_a[i, 0] = classify(f_a, a_a)

        for j, p in enumerate(p_vals):
            f_b = np.mean(np.array(data_b[b][p]['f_c_mean'])[-500:])
            a_b = np.mean(np.array(data_b[b][p]['a_max_mean'])[-500:])
            matrix[i, j] = classify(f_b, a_b)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    # Condition B heatmap
    cmap = LinearSegmentedColormap.from_list(
        'phase', ['#e74c3c', '#f39c12', '#3498db', '#2ecc71'], N=4)
    im = axes[0].imshow(matrix, cmap=cmap, vmin=0, vmax=3,
                         aspect='auto', origin='lower')
    axes[0].set_xticks(range(len(p_vals)))
    axes[0].set_xticklabels([f'$p={p:.1f}$' for p in p_vals])
    axes[0].set_yticks(range(len(b_vals)))
    axes[0].set_yticklabels([f'$b={b:.1f}$' for b in b_vals])
    axes[0].set_title('With Leviathan (Condition B)')

    # Annotate cells
    for i in range(len(b_vals)):
        for j in range(len(p_vals)):
            val = int(matrix[i, j])
            label = ['Defection', 'Fragmented', 'Clustered', 'Cooperation'][val]
            axes[0].text(j, i, label, ha='center', va='center',
                         fontsize=8, fontweight='bold',
                         color='white' if val in [0, 3] else 'black')

    # Condition A bar
    cmap_a = LinearSegmentedColormap.from_list(
        'phase_a', ['#e74c3c', '#f39c12', '#3498db', '#2ecc71'], N=4)
    bar_colors = [cmap_a(v / 3.0) for v in matrix_a.flatten()]
    axes[1].barh(range(len(b_vals)), [1] * len(b_vals), color=bar_colors,
                 edgecolor='white', linewidth=1.5, height=0.7)
    axes[1].set_yticks(range(len(b_vals)))
    axes[1].set_yticklabels([f'$b={b:.1f}$' for b in b_vals])
    axes[1].set_title('No Leviathan (Condition A)')
    axes[1].set_xticks([])

    # Colorbar — placed below both subplots via dedicated axes
    fig.subplots_adjust(bottom=0.22)
    cbar_ax = fig.add_axes([0.18, 0.06, 0.64, 0.035])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cbar.set_ticks([0.375, 1.125, 1.875, 2.625])
    cbar.set_ticklabels(['Defection', 'Fragmented', 'Clustered', 'Cooperation'])

    fig.suptitle('Phase Diagram — Final State Classification',
                 fontweight='bold', y=1.02)
    sns.despine()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig7_phase_diagram.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig7_phase_diagram.pdf'))
    plt.close(fig)
    print("  Figure 7 saved.")


# --------------------------------------------------------------------------
# Figure 8: Interface density & Cluster dynamics (Level 2)
# --------------------------------------------------------------------------

def fig8_interface_cluster(summary):
    """Interface density and largest cluster area — key dynamic metrics."""
    b_show = [1.4, 1.6, 1.8]

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))

    for j, b in enumerate(b_show):
        # Row 0: Interface density
        ax0 = axes[0, j]
        data_a = summary['A'][b]
        ax0.plot(data_a['time'], data_a['interface_density_mean'],
                 color=COLOR_NO_LEVIATHAN, linewidth=1.5, label='No Leviathan (A)',
                 linestyle='--')

        for p in sorted(summary['B'][b].keys()):
            data_b = summary['B'][b][p]
            ax0.plot(data_b['time'], data_b['interface_density_mean'],
                     color=COLOR_LEVIATHAN, linewidth=1.2, alpha=0.7,
                     label=f'$p={p:.1f}$')

        ax0.axvline(x=LEVIATHAN_TIME, color=COLOR_LEVIATHAN,
                    linestyle=':', linewidth=1, alpha=0.5)
        ax0.set_title(f'$b={b:.1f}$')
        if j == 0:
            ax0.set_ylabel('Interface density $\\rho(t)$')
        ax0.legend(fontsize=7)
        ax0.grid(True, alpha=0.3)

        # Row 1: Largest cluster area
        ax1 = axes[1, j]
        ax1.plot(data_a['time'], data_a['a_max_mean'],
                 color=COLOR_NO_LEVIATHAN, linewidth=1.5, label='No Leviathan (A)',
                 linestyle='--')

        for p in sorted(summary['B'][b].keys()):
            data_b = summary['B'][b][p]
            ax1.plot(data_b['time'], data_b['a_max_mean'],
                     color=COLOR_LEVIATHAN, linewidth=1.2, alpha=0.7,
                     label=f'$p={p:.1f}$')

        ax1.axvline(x=LEVIATHAN_TIME, color=COLOR_LEVIATHAN,
                    linestyle=':', linewidth=1, alpha=0.5)
        if j == 0:
            ax1.set_ylabel('Max cluster area $A_{max}(t)$')
        ax1.set_xlabel('Time step $t$')
        ax1.legend(fontsize=7)
        ax1.grid(True, alpha=0.3)

    fig.suptitle('Figure 8: Interface Dynamics & Cluster Growth (Level 2)',
                 fontweight='bold', y=1.01)
    sns.despine()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig8_interface_cluster.png'))
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig8_interface_cluster.pdf'))
    plt.close(fig)
    print("  Figure 8 saved.")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    print("Loading data...")
    summary_raw, meta = load_data()
    summary = _parse_summary(summary_raw)

    print(f"Grid: {meta['grid_size']}×{meta['grid_size']}, "
          f"Steps: {meta['total_steps']}, Reps: {meta['n_reps']}")
    print(f"b values: {meta['b_values']}")
    print(f"p values: {meta['p_values']}\n")

    print("Generating figures...")
    fig1_condition_a_timeseries(summary)
    fig2_ab_comparison(summary)
    fig3_full_grid(summary)
    fig4_spatial_snapshots()
    fig5_final_state(summary)
    fig6_trajectory_change(summary)
    fig7_phase_diagram(summary)
    fig8_interface_cluster(summary)

    print(f"\nAll figures saved to {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
