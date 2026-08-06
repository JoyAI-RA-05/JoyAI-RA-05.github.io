#!/usr/bin/env python3
"""Validate paper results and render project-page charts from one data file.

Role: Audit and render JoyAI-RA 0.5 quantitative results.
Status: Active source-of-truth generator for result SVG assets.
Inputs: data/experiment-results.json.
Outputs: assets/result-main-alignment.svg, assets/result-human-scaling.svg,
         assets/result-human-scaling-lacwm.svg,
         assets/result-human-scaling-policy.svg,
         assets/result-human-scaling-lacwm-light.svg,
         assets/result-human-scaling-policy-light.svg, assets/result-rl.svg,
         assets/result-rl-compact-light.svg, plus optional PNG previews.
Owner/module: JoyAI-RA 0.5 project page / results visualization.
Safe-to-delete/move: Do not delete while generated assets are used by the site.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DEFAULT_DATA = ROOT / "data" / "experiment-results.json"

# JoyAI-RA 0.1 project-page chart palette.
TEXT = "#f7faff"
MUTED = "#96a2bb"
MUTED_STRONG = "#c9d4eb"
GRID = "#d3dfff"
BLUE = "#73acd1"
RED = "#c0392b"
SLATE = "#59657d"
PANEL = "none"

# Main-benchmark palette follows the paper: the pi_0.5 baseline is blue,
# alignment ablations progress from light salmon to red, and the complete
# JoyAI-RA 0.5 model is solid dark red.
ABLATION_LIGHT = "#fcae91"
ABLATION_MID = "#fb6a4a"
ABLATION_DARK = "#ef3b2c"
OURS_RED = "#cb181d"
SCALING_COLORS = ["#f3c5a4", "#e9a064", "#e99087", "#d96a66"]
LIGHT_TEXT = "#20242c"
LIGHT_MUTED = "#626a78"
LIGHT_GRID = "#d8dde6"
LIGHT_BORDER = "#8e97a6"


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Alibaba PuHuiTi 3.0",
                "PingFang SC",
                "Microsoft YaHei",
                "Arial",
                "DejaVu Sans",
            ],
            "font.size": 13,
            "text.color": TEXT,
            "axes.labelcolor": TEXT,
            "axes.edgecolor": MUTED,
            "axes.facecolor": PANEL,
            "figure.facecolor": PANEL,
            "xtick.color": MUTED_STRONG,
            "ytick.color": MUTED_STRONG,
            "hatch.linewidth": 0.8,
            "svg.fonttype": "none",
        }
    )


def load_data(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def rounded_mean(values: list[float], digits: int) -> float:
    return round(sum(values) / len(values), digits)


def assert_close(actual: float, expected: float, label: str, tolerance: float = 0.051) -> None:
    if abs(actual - expected) > tolerance:
        raise ValueError(f"{label}: computed {actual}, reported {expected}")


def validate_data(data: dict[str, Any]) -> None:
    benchmark = data["main_benchmark"]
    for method in benchmark["methods"]:
        if len(method["seen"]) != len(benchmark["seen_categories"]):
            raise ValueError(f"{method['id']}: seen category/value length mismatch")
        if len(method["unseen"]) != len(benchmark["unseen_categories"]):
            raise ValueError(f"{method['id']}: unseen category/value length mismatch")
        assert_close(
            rounded_mean(method["seen"], 1),
            method["seen_average"],
            f"{method['id']} seen average",
        )
        assert_close(
            rounded_mean(method["unseen"], 1),
            method["unseen_average"],
            f"{method['id']} unseen average",
        )

    wm_rows = data["component_ablations"]["world_model"]["rows"]
    for row in wm_rows:
        assert_close(
            rounded_mean([row["seen"], row["unseen"]], 1),
            row["average"],
            f"{row['label']} average",
        )

    lac = data["human_video_scaling"]["lac_wm"]
    if not (len(lac["fractions"]) == len(lac["seen"]) == len(lac["unseen"]) == len(lac["average"])):
        raise ValueError("LAC-WM scaling series lengths do not match")
    for index, fraction in enumerate(lac["fractions"]):
        assert_close(
            rounded_mean([lac["seen"][index], lac["unseen"][index]], 2),
            lac["average"][index],
            f"LAC-WM {fraction}% average",
            tolerance=0.011,
        )

    policy = data["human_video_scaling"]["policy_pretraining"]
    if not (len(policy["fractions"]) == len(policy["seen"]) == len(policy["unseen"])):
        raise ValueError("Policy-scaling series lengths do not match")

    rl = data["reinforcement_learning"]
    if not (len(rl["strategies"]) == len(rl["mouse"]) == len(rl["headphone"])):
        raise ValueError("RL series lengths do not match")

    ours = next(item for item in benchmark["methods"] if item["id"] == "joyai_ra_05")
    baseline = next(item for item in benchmark["methods"] if item["id"] == "pi_05")
    assert_close(
        ours["seen_average"] - baseline["seen_average"],
        18.0,
        "JoyAI-RA 0.5 seen-average gain over pi_0.5",
        tolerance=0.001,
    )


def style_axis(ax: mpl.axes.Axes, title: str) -> None:
    ax.set_title(title, loc="center", fontsize=21, fontweight="bold", pad=24, color=TEXT)
    ax.set_ylim(0, 105)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("Task Score", fontsize=12.5, fontweight="bold", labelpad=10)
    ax.grid(axis="y", color=GRID, linewidth=1.0, alpha=0.16, linestyle=(0, (4, 4)))
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MUTED)
    ax.spines[["left", "bottom"]].set_alpha(0.52)
    ax.spines[["left", "bottom"]].set_linewidth(1.15)
    ax.tick_params(axis="x", length=0, pad=11)
    ax.tick_params(axis="y", length=0, pad=8)


def style_light_axis(ax: mpl.axes.Axes, title: str) -> None:
    """Style the policy-scaling chart to match the adjacent paper figure."""
    ax.set_facecolor("#ffffff")
    ax.set_title(title, loc="center", fontsize=21, fontweight="bold", pad=24, color=LIGHT_TEXT)
    ax.set_ylim(0, 105)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("Task Score", fontsize=12.5, fontweight="bold", labelpad=10, color=LIGHT_TEXT)
    ax.grid(axis="y", color=LIGHT_GRID, linewidth=1.0, alpha=0.9, linestyle=(0, (4, 4)))
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(LIGHT_BORDER)
    ax.spines[["left", "bottom"]].set_linewidth(1.15)
    ax.tick_params(axis="x", colors=LIGHT_MUTED, length=0, pad=11)
    ax.tick_params(axis="y", colors=LIGHT_MUTED, length=0, pad=8)


def style_compact_light_axis(ax: mpl.axes.Axes, title: str) -> None:
    """Use larger labels and tighter spacing for charts shown at 60% width."""
    style_light_axis(ax, title)
    ax.set_title(title, loc="center", fontsize=18.5, fontweight="bold", pad=17, color=LIGHT_TEXT)
    ax.set_ylabel("Task Score", fontsize=11.5, fontweight="bold", labelpad=8, color=LIGHT_TEXT)
    ax.tick_params(axis="x", labelsize=11.5, pad=9)
    ax.tick_params(axis="y", labelsize=10.5, pad=7)


def add_values(
    ax: mpl.axes.Axes,
    bars,
    *,
    fontsize: float = 8.5,
    color: str = MUTED_STRONG,
) -> None:
    for bar in bars:
        value = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1.35,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=fontsize,
            color=color,
            fontweight="bold",
        )


def save(fig: mpl.figure.Figure, filename: str, preview_dir: Path | None) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    output_path = ASSETS / filename
    fig.savefig(output_path, format="svg", bbox_inches="tight", transparent=True)
    # Matplotlib emits trailing spaces in multiline SVG paths; normalize the
    # generated asset so repository whitespace checks remain meaningful.
    svg = output_path.read_text(encoding="utf-8")
    output_path.write_text(
        "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
        encoding="utf-8",
    )
    if preview_dir:
        preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            preview_dir / filename.replace(".svg", ".png"),
            dpi=170,
            bbox_inches="tight",
            transparent=True,
        )
    plt.close(fig)


def main_alignment(data: dict[str, Any], preview_dir: Path | None) -> None:
    benchmark = data["main_benchmark"]
    methods = benchmark["methods"]
    seen_labels = benchmark["seen_categories"] + ["Average"]
    unseen_labels = [label.replace(" & ", " &\n") for label in benchmark["unseen_categories"]] + ["Average"]
    seen = np.array([item["seen"] + [item["seen_average"]] for item in methods])
    unseen = np.array([item["unseen"] + [item["unseen_average"]] for item in methods])

    styles = {
        "pi_05": {"color": BLUE, "hatch": None, "edgecolor": "none"},
        "without_both": {"color": ABLATION_LIGHT, "hatch": "////", "edgecolor": TEXT},
        "without_implicit": {"color": ABLATION_MID, "hatch": "////", "edgecolor": TEXT},
        "without_explicit": {"color": ABLATION_DARK, "hatch": "////", "edgecolor": TEXT},
        "joyai_ra_05": {"color": OURS_RED, "hatch": None, "edgecolor": "none"},
    }

    fig, axes = plt.subplots(1, 2, figsize=(16, 5.55), gridspec_kw={"wspace": 0.13})
    fig.subplots_adjust(top=0.86, bottom=0.22, left=0.06, right=0.985)
    width = 0.155
    x = np.arange(4)
    for ax, title, labels, values in zip(
        axes,
        ["Seen Performance", "Unseen Generalization"],
        [seen_labels, unseen_labels],
        [seen, unseen],
    ):
        style_axis(ax, title)
        for index, method in enumerate(methods):
            style = styles[method["id"]]
            bars = ax.bar(
                x + (index - 2) * width,
                values[index],
                width=width * 0.9,
                label=method["label"],
                color=style["color"],
                hatch=style["hatch"],
                edgecolor=style["edgecolor"],
                linewidth=0.7 if style["hatch"] else 0,
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
        bbox_to_anchor=(0.5, 0.015),
        fontsize=10.5,
        handlelength=1.5,
    )
    for label in legend.get_texts():
        label.set_color(MUTED_STRONG)
    save(fig, "result-main-alignment.svg", preview_dir)


def main_alignment_split(data: dict[str, Any], preview_dir: Path | None) -> None:
    """Render independently selectable seen and unseen benchmark panels."""
    benchmark = data["main_benchmark"]
    methods = benchmark["methods"]
    styles = {
        "pi_05": {"color": BLUE, "hatch": None, "edgecolor": "none"},
        "without_both": {"color": ABLATION_LIGHT, "hatch": "////", "edgecolor": LIGHT_TEXT},
        "without_implicit": {"color": ABLATION_MID, "hatch": "////", "edgecolor": LIGHT_TEXT},
        "without_explicit": {"color": ABLATION_DARK, "hatch": "////", "edgecolor": LIGHT_TEXT},
        "joyai_ra_05": {"color": OURS_RED, "hatch": None, "edgecolor": "none"},
    }

    panels = [
        (
            "seen",
            "Seen Performance",
            benchmark["seen_categories"] + ["Average"],
            np.array([item["seen"] + [item["seen_average"]] for item in methods]),
            "result-main-alignment-seen-light.svg",
        ),
        (
            "unseen",
            "Unseen Generalization",
            [label.replace(" & ", " &\n") for label in benchmark["unseen_categories"]] + ["Average"],
            np.array([item["unseen"] + [item["unseen_average"]] for item in methods]),
            "result-main-alignment-unseen-light.svg",
        ),
    ]

    for _key, title, labels, values, filename in panels:
        fig, ax = plt.subplots(figsize=(8.4, 5.8))
        fig.subplots_adjust(top=0.86, bottom=0.29, left=0.11, right=0.985)
        style_compact_light_axis(ax, title)
        width = 0.155
        x = np.arange(4)
        for index, method in enumerate(methods):
            style = styles[method["id"]]
            bars = ax.bar(
                x + (index - 2) * width,
                values[index],
                width=width * 0.9,
                label=method["label"],
                color=style["color"],
                hatch=style["hatch"],
                edgecolor=style["edgecolor"],
                linewidth=0.7 if style["hatch"] else 0,
            )
            add_values(ax, bars, fontsize=8.8, color=LIGHT_TEXT)
        ax.set_xticks(x, labels)

        legend = ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.19),
            ncol=2,
            frameon=False,
            fontsize=9.8,
            handlelength=1.4,
            columnspacing=1.4,
        )
        for label in legend.get_texts():
            label.set_color(LIGHT_MUTED)
        save(fig, filename, preview_dir)


def human_scaling_split_light(data: dict[str, Any], preview_dir: Path | None) -> None:
    """Render the two human-video scaling studies as selectable light panels."""
    scaling = data["human_video_scaling"]
    panels = [
        (
            "LAC-WM Pretraining",
            scaling["lac_wm"],
            "result-human-scaling-lacwm-light.svg",
        ),
        (
            "Policy Pretraining",
            scaling["policy_pretraining"],
            "result-human-scaling-policy-light.svg",
        ),
    ]

    for title, result, filename in panels:
        fig, ax = plt.subplots(figsize=(8.4, 5.35))
        fig.subplots_adjust(top=0.85, bottom=0.25, left=0.11, right=0.985)
        style_compact_light_axis(ax, title)

        labels = [f"{fraction}%" for fraction in result["fractions"]]
        x = np.arange(len(labels))
        width = 0.32
        seen_bars = ax.bar(x - width / 2, result["seen"], width, color=BLUE, label="Seen")
        unseen_bars = ax.bar(
            x + width / 2,
            result["unseen"],
            width,
            color=OURS_RED,
            label="Unseen",
        )
        add_values(ax, seen_bars, fontsize=10.5, color=LIGHT_TEXT)
        add_values(ax, unseen_bars, fontsize=10.5, color=LIGHT_TEXT)
        ax.set_xticks(x, labels)
        ax.set_xlabel(
            "Human Video Fraction",
            fontsize=11,
            fontweight="bold",
            labelpad=13,
            color=LIGHT_TEXT,
        )

        legend = ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.17),
            ncol=2,
            frameon=False,
            fontsize=11,
            handlelength=1.5,
            columnspacing=1.8,
        )
        for label in legend.get_texts():
            label.set_color(LIGHT_MUTED)
        save(fig, filename, preview_dir)


def human_scaling(data: dict[str, Any], preview_dir: Path | None) -> None:
    scaling = data["human_video_scaling"]
    panels = [
        ("LAC-WM Pretraining", scaling["lac_wm"]),
        ("Policy Pretraining", scaling["policy_pretraining"]),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(16, 5.25), gridspec_kw={"wspace": 0.14})
    fig.subplots_adjust(top=0.85, bottom=0.2, left=0.06, right=0.985)
    for ax, (title, result) in zip(axes, panels):
        style_axis(ax, title)
        labels = [f"{fraction}%" for fraction in result["fractions"]]
        x = np.arange(len(labels))
        width = 0.32
        seen_bars = ax.bar(x - width / 2, result["seen"], width, color=BLUE, label="Seen")
        unseen_bars = ax.bar(x + width / 2, result["unseen"], width, color=RED, label="Unseen")
        add_values(ax, seen_bars, fontsize=10)
        add_values(ax, unseen_bars, fontsize=10)
        ax.set_xticks(x, labels)
        ax.set_xlabel("Human Video Fraction", fontsize=12, fontweight="bold", labelpad=14)

    handles, labels = axes[0].get_legend_handles_labels()
    legend = fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.01),
        fontsize=11.5,
    )
    for label in legend.get_texts():
        label.set_color(MUTED_STRONG)
    save(fig, "result-human-scaling.svg", preview_dir)

    for filename, title, result in [
        ("result-human-scaling-lacwm.svg", "LAC-WM Performance vs Data Amount", scaling["lac_wm"]),
        ("result-human-scaling-policy.svg", "Policy Performance vs Data Amount", scaling["policy_pretraining"]),
    ]:
        fractions = result["fractions"]
        x = np.arange(len(fractions))
        colors = SCALING_COLORS if len(fractions) == 4 else [SCALING_COLORS[0], SCALING_COLORS[1], SCALING_COLORS[3]]

        is_policy_panel = filename.endswith("policy.svg")
        fig, ax = plt.subplots(figsize=(7.2, 6.2) if is_policy_panel else (10.8, 5.5))
        if is_policy_panel:
            fig.subplots_adjust(top=0.85, bottom=0.17, left=0.14, right=0.97)
        else:
            fig.subplots_adjust(top=0.84, bottom=0.19, left=0.09, right=0.98)
        if is_policy_panel:
            fig.patch.set_facecolor("#ffffff")
            style_light_axis(ax, title)
        else:
            style_axis(ax, title)
        width = 0.48

        line_primary = LIGHT_TEXT if is_policy_panel else TEXT
        line_secondary = RED if is_policy_panel else MUTED_STRONG
        marker_face = "#ffffff" if is_policy_panel else PANEL
        value_color = LIGHT_TEXT if is_policy_panel else TEXT
        edge_color = "#b7bec9" if is_policy_panel else MUTED_STRONG

        # Match the paper: the saturated unseen bar overlays the lighter seen bar,
        # while marker lines make both trends explicit across data fractions.
        ax.bar(
            x,
            result["seen"],
            width,
            color=[mpl.colors.to_rgba(color, 0.38) for color in colors],
            edgecolor=edge_color,
            linewidth=1.0,
            zorder=2,
        )
        ax.bar(
            x,
            result["unseen"],
            width,
            color=colors,
            edgecolor=edge_color,
            linewidth=1.0,
            zorder=3,
        )
        ax.plot(
            x,
            result["seen"],
            color=line_primary,
            linewidth=2.0,
            marker="o",
            markersize=7,
            markerfacecolor=marker_face,
            markeredgecolor=line_primary,
            markeredgewidth=1.5,
            zorder=4,
        )
        ax.plot(
            x,
            result["unseen"],
            color=line_secondary,
            linewidth=2.0,
            marker="s",
            markersize=6.5,
            markerfacecolor=marker_face,
            markeredgecolor=line_secondary,
            markeredgewidth=1.5,
            zorder=4,
        )
        for index, (seen, unseen) in enumerate(zip(result["seen"], result["unseen"])):
            ax.text(
                index,
                seen + 2.2,
                f"{seen:.1f}",
                ha="center",
                va="bottom",
                color=value_color,
                fontsize=10.5,
                fontweight="bold",
            )
            ax.text(
                index,
                unseen - 2.7,
                f"{unseen:.1f}",
                ha="center",
                va="top",
                color=value_color,
                fontsize=10.5,
                fontweight="bold",
            )

        ax.set_xticks(x, [f"{fraction}%" for fraction in fractions])
        ax.set_xlabel(
            "Human Video Fraction",
            fontsize=12,
            fontweight="bold",
            labelpad=14,
            color=LIGHT_TEXT if is_policy_panel else TEXT,
        )
        legend = ax.legend(
            handles=[
                Line2D([0], [0], color=line_primary, marker="o", markerfacecolor=marker_face, label="Seen"),
                Line2D([0], [0], color=line_secondary, marker="s", markerfacecolor=marker_face, label="Unseen"),
            ],
            loc="upper left",
            frameon=False,
            fontsize=11.5,
        )
        for label in legend.get_texts():
            label.set_color(LIGHT_MUTED if is_policy_panel else MUTED_STRONG)
        save(fig, filename, preview_dir)


def rl_results(data: dict[str, Any], preview_dir: Path | None) -> None:
    results = data["reinforcement_learning"]
    labels = [
        "Original VLWA\nPolicy",
        "Inner-loop\nRL Only",
        "Outer-loop\nRL Only",
        "Inner-outer Loop\nRL",
    ]

    fig, ax = plt.subplots(figsize=(14, 5.05))
    fig.subplots_adjust(top=0.9, bottom=0.22, left=0.075, right=0.975)
    style_axis(ax, "Success Rate under Unseen Object-Position Shifts")
    ax.set_ylabel("Task Success Rate (%)", fontsize=12.5, fontweight="bold", labelpad=10)
    x = np.arange(len(labels))
    width = 0.31
    mouse_bars = ax.bar(x - width / 2, results["mouse"], width, color=BLUE, label="Mouse")
    headphone_bars = ax.bar(x + width / 2, results["headphone"], width, color=RED, label="Headphone")
    add_values(ax, mouse_bars, fontsize=10.5)
    add_values(ax, headphone_bars, fontsize=10.5)
    ax.set_xticks(x, labels)
    legend = ax.legend(loc="upper left", frameon=False, ncol=2, fontsize=11.5)
    for label in legend.get_texts():
        label.set_color(MUTED_STRONG)
    save(fig, "result-rl.svg", preview_dir)


def rl_results_compact_light(data: dict[str, Any], preview_dir: Path | None) -> None:
    """Render the RL comparison for the narrower results column."""
    results = data["reinforcement_learning"]
    labels = [
        "Original VLWA\nPolicy",
        "Inner-loop RL\nOnly",
        "Outer-loop RL\nOnly",
        "Inner–Outer Loop\nRL",
    ]

    fig, ax = plt.subplots(figsize=(8.4, 5.35))
    fig.subplots_adjust(top=0.85, bottom=0.22, left=0.12, right=0.985)
    style_compact_light_axis(ax, "Success Rate under Unseen Position Shifts")
    ax.set_ylabel(
        "Task Success Rate (%)",
        fontsize=11.5,
        fontweight="bold",
        labelpad=8,
        color=LIGHT_TEXT,
    )
    x = np.arange(len(labels))
    width = 0.31
    mouse_bars = ax.bar(x - width / 2, results["mouse"], width, color=BLUE, label="Mouse")
    headphone_bars = ax.bar(
        x + width / 2,
        results["headphone"],
        width,
        color=OURS_RED,
        label="Headphone",
    )
    add_values(ax, mouse_bars, fontsize=10.5, color=LIGHT_TEXT)
    add_values(ax, headphone_bars, fontsize=10.5, color=LIGHT_TEXT)
    ax.set_xticks(x, labels)
    legend = ax.legend(loc="upper left", frameon=False, ncol=2, fontsize=11)
    for label in legend.get_texts():
        label.set_color(LIGHT_MUTED)
    save(fig, "result-rl-compact-light.svg", preview_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Result data JSON.")
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Optionally write transparent PNG previews to this directory.",
    )
    parser.add_argument("--check-only", action="store_true", help="Validate data without rendering charts.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = load_data(args.data)
    validate_data(data)
    print(f"Verified experiment results: {args.data}")
    if args.check_only:
        return
    configure()
    main_alignment(data, args.preview_dir)
    main_alignment_split(data, args.preview_dir)
    human_scaling(data, args.preview_dir)
    human_scaling_split_light(data, args.preview_dir)
    rl_results(data, args.preview_dir)
    rl_results_compact_light(data, args.preview_dir)


if __name__ == "__main__":
    main()
