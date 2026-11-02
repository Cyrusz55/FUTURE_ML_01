from pathlib import Path

import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "outputs" / "powerbi_model_comparison.csv"
IMAGE_PATH = ROOT / "docs" / "images" / "model_comparison.png"
PALETTE = ["#1f2937", "#0F4D92", "#d97706", "#9ca3af", "#b91c1c"]


def main() -> None:
    if not CSV_PATH.exists():
        return

    data = pd.read_csv(CSV_PATH)
    data["WAPE"] = data["WAPE"] * 100
    levels = ["Store and family", "Chain total", "Store 44"]
    titles = ["Store and family", "Chain total", "Single store"]

    figure, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor="white")
    for axis, level, title in zip(axes, levels, titles):
        level_data = data[data["level"] == level]
        averages = level_data.groupby("model", sort=False)["WAPE"].mean()
        colors = [PALETTE[index % len(PALETTE)] for index in range(len(averages))]
        bars = axis.bar(averages.index, averages.values, color=colors)
        axis.set_title(title)
        axis.set_ylabel("Average WAPE percent")
        axis.tick_params(axis="x", labelrotation=55)
        axis.grid(axis="y", alpha=0.25)
        axis.set_axisbelow(True)
        for bar, value in zip(bars, averages.values):
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                value,
                f"{value:.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    figure.suptitle("Average WAPE across four validation folds", fontsize=15)
    figure.tight_layout()
    IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(IMAGE_PATH, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(figure)


if __name__ == "__main__":
    main()
