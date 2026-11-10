#!/usr/bin/env python3
"""
charts.py - clean, board-ready safety charts (PNG). One visual language across every Frontline output.

from charts import trend_chart, pareto_chart, risk_heatmap, hotspot_bars
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

INK, MUTED, GRID = "#1F2430", "#6B7280", "#E5E7EB"
ACCENT, ACCENT_SOFT = "#5B47E0", "#C9C2F7"
RAG = {"Low": "#2E9E5B", "Medium": "#F2B705", "High": "#E8710A", "Extreme": "#C62828"}

def _style(ax, title, subtitle=None):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=INK, pad=22 if subtitle else 10)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9, color=MUTED)

def trend_chart(periods, values, path, title, subtitle=None, target=None, rolling=None, ylabel=None):
    """Bar per period with optional rolling line and target line. Keep titles as findings, e.g.
    'TRIFR down 18% on last quarter, still above target'."""
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
    ax.bar(periods, values, color=ACCENT_SOFT, width=0.6, label="Period")
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:g}", ha="center", va="bottom", fontsize=8, color=INK)
    if rolling is not None:
        ax.plot(periods, rolling, color=ACCENT, linewidth=2.2, marker="o", markersize=4, label="Rolling")
    if target is not None:
        ax.axhline(target, color=RAG["Extreme"], linestyle="--", linewidth=1.2)
        ax.text(len(periods) - 0.5, target, f" Target {target:g}", color=RAG["Extreme"], fontsize=8, va="bottom", ha="right")
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    _style(ax, title, subtitle)
    if rolling is not None:
        ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return path

def pareto_chart(categories, counts, path, title, subtitle=None):
    pairs = sorted(zip(categories, counts), key=lambda x: -x[1])
    cats, vals = [p[0] for p in pairs], [p[1] for p in pairs]
    total = sum(vals) or 1
    cum, run = [], 0
    for v in vals:
        run += v; cum.append(run / total * 100)
    fig, ax = plt.subplots(figsize=(8, 4.4), dpi=200)
    ax.bar(range(len(cats)), vals, color=[ACCENT if c <= 80 else ACCENT_SOFT for c in cum], width=0.6)
    ax.set_xticks(range(len(cats))); ax.set_xticklabels(cats, rotation=30, ha="right", fontsize=8)
    ax2 = ax.twinx(); ax2.plot(range(len(cats)), cum, color=INK, marker="o", markersize=3, linewidth=1.5)
    ax2.set_ylim(0, 105); ax2.axhline(80, color=MUTED, linestyle=":", linewidth=1)
    ax2.tick_params(colors=MUTED, labelsize=8); ax2.spines["top"].set_visible(False)
    _style(ax, title, subtitle)
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return path

def band(score, bands=((1, 4, "Low"), (5, 9, "Medium"), (10, 14, "High"), (15, 25, "Extreme"))):
    for lo, hi, name in bands:
        if lo <= score <= hi:
            return name
    return "Extreme"

def risk_heatmap(cell_counts, path, title, subtitle=None, bands=None):
    """cell_counts: dict {(likelihood 1-5, consequence 1-5): n}. Draws a 5x5 matrix, count in each cell."""
    fig, ax = plt.subplots(figsize=(5.6, 5.0), dpi=200)
    for L in range(1, 6):
        for C in range(1, 6):
            b = band(L * C) if bands is None else band(L * C, bands)
            ax.add_patch(Rectangle((C - 1, L - 1), 1, 1, facecolor=RAG[b], alpha=0.85, edgecolor="white", linewidth=2))
            n = cell_counts.get((L, C), 0)
            if n:
                ax.text(C - 0.5, L - 0.5, str(n), ha="center", va="center", fontsize=15, fontweight="bold", color="white")
    ax.set_xlim(0, 5); ax.set_ylim(0, 5)
    ax.set_xticks([i + 0.5 for i in range(5)]); ax.set_xticklabels(["Insignificant", "Minor", "Moderate", "Major", "Catastrophic"], fontsize=8, color=MUTED)
    ax.set_yticks([i + 0.5 for i in range(5)]); ax.set_yticklabels(["Rare", "Unlikely", "Possible", "Likely", "Almost\ncertain"], fontsize=8, color=MUTED)
    ax.set_xlabel("Consequence", color=MUTED, fontsize=9); ax.set_ylabel("Likelihood", color=MUTED, fontsize=9)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=INK, pad=22 if subtitle else 10)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=8.5, color=MUTED)
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return path

def hotspot_bars(labels, values, path, title, subtitle=None, highlight=None):
    """Horizontal bars, largest first. highlight = label(s) to colour as the finding."""
    pairs = sorted(zip(labels, values), key=lambda x: x[1])
    hl = set([highlight] if isinstance(highlight, str) else (highlight or []))
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(pairs) + 1.4), dpi=200)
    ax.barh([p[0] for p in pairs], [p[1] for p in pairs], color=[ACCENT if p[0] in hl else ACCENT_SOFT for p in pairs], height=0.6)
    for i, p in enumerate(pairs):
        ax.text(p[1], i, f" {p[1]:g}", va="center", fontsize=8, color=INK)
    _style(ax, title, subtitle); ax.xaxis.grid(True, color=GRID); ax.yaxis.grid(False)
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)
    return path
