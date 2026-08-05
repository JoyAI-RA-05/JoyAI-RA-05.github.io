#!/usr/bin/env python3
"""Generate the project-page experiment charts from paper-reported values.

Role: Render publication results in the JoyAI-RA 0.5 web visual system.
Status: Active source-of-truth generator for result SVG assets.
Inputs: Experiment values transcribed from the latest Overleaf project.
Outputs: assets/result-main-alignment.svg, assets/result-human-scaling.svg,
         assets/result-rl.svg, plus optional PNG previews.
Owner/module: JoyAI-RA 0.5 project page / results visualization.
Safe-to-delete/move: Do not delete while generated assets are used by the site.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

BG = "#0d1220"
PANEL = "#111827"
TEXT = "#eef3ff"
MUTED = "#a7b0c4"
GRID = "#2a3550"
RED = "#f21b1b"
CYAN = "#07c8f8"
VIOLET = "#725cff"
BASELINE = "#75819a"
CORAL = "#ff7668"
PURPLE = "#a077ff"


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 13,
            "text.color": TEXT,
            "axes.labelcolor": MUTED,
            "axes.edgecolor": GRID,
            "axes.facecolor": PANEL,
            "figure.facecolor": BG,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "svg.fonttype": "none",
        }
    )


def style_axis(ax: mpl.axes.Axes, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=21, fontweight="bold", pad=20, color=TEXT)
    ax.set_ylim(0, 108)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Task score", fontsize=12, fontweight="bold")
    ax.grid(axis="y", color=GRID, linewidth=0.9, alpha=0.72)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="x", length=0, pad=10)
    ax.tick_params(axis="y", length=0)


def add_values(ax: mpl.axes.Axes, bars, *, fontsize: float = 8.5) -> None:
    for bar in bars:
        value = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1.4,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color=TEXT,
            fontweight="bold",
        )


def save(fig: mpl.figure.Figure, filename: str, preview_dir: Path | None) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / filename, format="svg", bbox_inches="tight", facecolor=BG)
    if preview_dir:
        preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            preview_dir / filename.replace(".svg", ".png"),
            dpi=150,
            bbox_inches="tight",
            facecolor=BG,
        )
    plt.close(fig)


def main_alignment(preview_dir: Path | None) -> None:
    methods = [
        r"$\pi_{0.5}$",
        "No alignment",
        "No implicit",
        "No explicit",
        "JoyAI-RA 0.5",
    ]
    colors = [BASELINE, PURPLE, CORAL, CYAN, RED]
    seen_labels = ["PnP Easy", "PnP Hard", "Long-Horizon", "Average"]
    unseen_labels = ["Spatial &\ntopological", "Object &\nattribute", "Background &\nillumination", "Average"]
    seen = np.array(
        [
            [83.0, 75.5, 63.5, 74.0],
            [93.0, 67.5, 51.6, 70.7],
            [96.0, 80.5, 83.0, 86.5],
            [97.0, 80.3, 79.8, 85.7],
            [98.0, 94.2, 83.8, 92.0],
        ]
    )
    unseen = np.array(
        [
            [79.6, 76.0, 61.9, 72.5],
            [36.4, 31.2, 21.8, 29.8],
            [49.4, 63.5, 27.5, 46.8],
            [66.6, 66.6, 69.2, 67.5],
            [77.6, 79.1, 69.8, 75.5],
        ]
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 7.2), gridspec_kw={"wspace": 0.12})
    fig.subplots_adjust(top=0.82, bottom=0.18, left=0.06, right=0.985)
    fig.suptitle(
        "Real-World Performance and Dual-Alignment Ablation",
        x=0.06,
        y=0.97,
        ha="left",
        fontsize=27,
        fontweight="bold",
        color=TEXT,
    )
    fig.text(
        0.06,
        0.905,
        "JoyAI-RA 0.5 is strongest overall; removing either alignment channel reduces transfer, especially under novel conditions.",
        color=MUTED,
        fontsize=13.5,
    )

    width = 0.155
    x = np.arange(4)
    for ax, title, labels, data in zip(
        axes,
        ["Seen performance", "Unseen generalization"],
        [seen_labels, unseen_labels],
        [seen, unseen],
    ):
        style_axis(ax, title)
        for idx, (method, color) in enumerate(zip(methods, colors)):
            bars = ax.bar(
                x + (idx - 2) * width,
                data[idx],
                width=width * 0.9,
                label=method,
                color=color,
                alpha=1 if idx == 4 else 0.82,
                edgecolor="none",
            )
            add_values(ax, bars, fontsize=7.6)
        ax.set_xticks(x, labels)

    handles, labels = axes[0].get_legend_handles_labels()
    legend = fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=5,
        frameon=False,
        bbox_to_anchor=(0.5, 0.02),
        fontsize=11.5,
        handlelength=1.4,
    )
    for text in legend.get_texts():
        text.set_color(MUTED)
    save(fig, "result-main-alignment.svg", preview_dir)


def human_scaling(preview_dir: Path | None) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6.8), gridspec_kw={"wspace": 0.14})
    fig.subplots_adjust(top=0.8, bottom=0.17, left=0.06, right=0.985)
    fig.suptitle(
        "Human Video Scaling",
        x=0.06,
        y=0.96,
        ha="left",
        fontsize=27,
        fontweight="bold",
        color=TEXT,
    )
    fig.text(
        0.06,
        0.89,
        "Increasing egocentric video consistently strengthens learned dynamics and downstream robot control.",
        color=MUTED,
        fontsize=13.5,
    )

    panels = [
        ("LAC-WM pretraining", ["10%", "25%", "100%"], [83.1, 89.4, 97.5], [56.9, 67.7, 72.4]),
        ("Policy pretraining", ["10%", "25%", "50%", "100%"], [47.8, 75.3, 80.5, 85.6], [37.6, 53.4, 58.6, 60.2]),
    ]
    for ax, (title, labels, seen, unseen) in zip(axes, panels):
        style_axis(ax, title)
        x = np.arange(len(labels))
        width = 0.32
        seen_bars = ax.bar(x - width / 2, seen, width, color=RED, label="Seen")
        unseen_bars = ax.bar(x + width / 2, unseen, width, color=CYAN, label="Unseen")
        add_values(ax, seen_bars, fontsize=10)
        add_values(ax, unseen_bars, fontsize=10)
        ax.set_xticks(x, labels)
        ax.set_xlabel("EgoLive data used", fontsize=12, fontweight="bold", labelpad=13)

    handles, labels = axes[0].get_legend_handles_labels()
    legend = fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.015),
        fontsize=12,
    )
    for text in legend.get_texts():
        text.set_color(MUTED)
    save(fig, "result-human-scaling.svg", preview_dir)


def rl_results(preview_dir: Path | None) -> None:
    strategies = ["Original VLWA", "Inner loop", "Outer loop", "Inner–outer loop"]
    mouse = [25.0, 45.0, 60.0, 70.0]
    headphone = [25.0, 35.0, 40.0, 50.0]

    fig, ax = plt.subplots(figsize=(14, 6.4))
    fig.subplots_adjust(top=0.76, bottom=0.2, left=0.075, right=0.975)
    fig.suptitle(
        "Inner–Outer Loop Reinforcement Learning",
        x=0.075,
        y=0.955,
        ha="left",
        fontsize=27,
        fontweight="bold",
        color=TEXT,
    )
    fig.text(
        0.075,
        0.875,
        "Success rate under unseen object-position shifts",
        color=MUTED,
        fontsize=13.5,
    )
    style_axis(ax, "Real-world pick-and-place")
    x = np.arange(len(strategies))
    width = 0.31
    mouse_bars = ax.bar(x - width / 2, mouse, width, color=RED, label="Mouse")
    headphone_bars = ax.bar(x + width / 2, headphone, width, color=CYAN, label="Headphone")
    add_values(ax, mouse_bars, fontsize=11)
    add_values(ax, headphone_bars, fontsize=11)
    ax.set_xticks(x, strategies)
    legend = ax.legend(loc="upper left", frameon=False, ncol=2, fontsize=12)
    for text in legend.get_texts():
        text.set_color(MUTED)
    save(fig, "result-rl.svg", preview_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Optionally write PNG previews to this directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure()
    main_alignment(args.preview_dir)
    human_scaling(args.preview_dir)
    rl_results(args.preview_dir)


if __name__ == "__main__":
    main()
