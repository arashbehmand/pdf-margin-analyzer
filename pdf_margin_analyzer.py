#!/usr/bin/env python3
"""
pdf_margin_analyzer.py: A CLI tool to analyze and adjust margins in PDF documents.

This script provides functionality to detect margins in PDF documents,
calculate statistics, plot margin distributions, and optionally adjust
margins to desired values.

Author: Arash Behmand
Date: 2024-07-01
"""

import argparse
import fitz  # PyMuPDF
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns


def get_bounding_box(page):
    """
    Get the bounding box of the content in a page.

    Args:
        page (fitz.Page): A page object from PyMuPDF.

    Returns:
        dict: A dictionary containing normalized coordinates of the bounding box.
    """
    rect = page.rect
    text_blocks = page.get_text("blocks")

    if not text_blocks:
        return {"left": np.NaN, "top": np.NaN, "right": np.NaN, "bottom": np.NaN}

    x0 = min(block[0] for block in text_blocks)
    y0 = min(block[1] for block in text_blocks)
    x1 = max(block[2] for block in text_blocks)
    y1 = max(block[3] for block in text_blocks)

    return {
        "left": x0 / rect.width,
        "top": y0 / rect.height,
        "right": (rect.width - x1) / rect.width,
        "bottom": (rect.height - y1) / rect.height,
    }


def calculate_margins(pages, exception_list, inner_outer=False):
    """
    Calculate margins for odd and even pages.

    Args:
        pages (list): List of fitz.Page objects.
        exception_list (list): List of page numbers to exclude (0-based index).
        inner_outer (bool): If True, use inner/outer instead of left/right.

    Returns:
        list: List of dictionaries containing margin information for each page.
    """
    margins = []

    for i, page in enumerate(pages):
        if i in exception_list:
            continue
        bbox = get_bounding_box(page)
        if inner_outer:
            if (i + 1) % 2 == 0:
                bbox["inner"] = bbox.pop("left")
                bbox["outer"] = bbox.pop("right")
            else:
                bbox["inner"] = bbox.pop("right")
                bbox["outer"] = bbox.pop("left")
        margins.append(bbox)

    return margins


def calculate_iqr(data):
    """
    Calculate the Interquartile Range (IQR) for a list of data.

    Args:
        data (list): List of numerical data.

    Returns:
        float: The Interquartile Range.
    """
    q75, q25 = np.percentile(data, [75, 25])
    return q75 - q25


def statistics_margins(margins):
    """
    Calculate various statistics from a list of margins.

    Args:
        margins (list): List of dictionaries containing margin information.

    Returns:
        dict: Dictionary containing statistics for each margin type.
    """
    if not margins:
        return None

    statistics = {}
    for key in margins[0]:
        data = [margin[key] for margin in margins if not np.isnan(margin[key])]
        statistics[key] = {
            "min": np.min(data),
            "max": np.max(data),
            "mean": np.mean(data),
            "median": np.median(data),
            "iqr": calculate_iqr(data),
            "stddev": np.std(data),
        }

    return statistics


def print_margins(margins, label):
    """
    Print margins in a formatted way.

    Args:
        margins (dict): Dictionary containing margin statistics.
        label (str): Label for the margins being printed.
    """
    if margins:
        print(f"{label} margins (percentage):")
        for key in margins:
            print(f"  {key.capitalize()}:")
            print(f"    Min: {margins[key]['min'] * 100:.2f}%")
            print(f"    Max: {margins[key]['max'] * 100:.2f}%")
            print(f"    Mean: {margins[key]['mean'] * 100:.2f}%")
            print(f"    Median: {margins[key]['median'] * 100:.2f}%")
            print(f"    IQR: {margins[key]['iqr'] * 100:.2f}%")
            print(f"    StdDev: {margins[key]['stddev'] * 100:.2f}%")
    else:
        print(f"No {label.lower()} pages to calculate margins.")


def plot_margins(margins):
    """
    Plot the margins using a violin plot.

    Args:
        margins (list): List of dictionaries containing margin information.
    """
    if not margins:
        return

    # Prepare data for plotting
    data = {
        key: [margin[key] for margin in margins if not np.isnan(margin[key])]
        for key in margins[0]
    }

    # Create a violin plot for each margin
    fig, axes = plt.subplots(1, 4, figsize=(20, 6))
    fig.suptitle("Margins Statistics")

    for i, key in enumerate(data):
        sns.violinplot(data=data[key], ax=axes[i], inner="quart")
        axes[i].set_title(key.capitalize())
        axes[i].set_xlabel("Percentage")
        axes[i].set_ylabel("Value")

        # Add statistics to the plot
        stats = statistics_margins(margins)
        axes[i].axhline(
            stats[key]["mean"],
            color="r",
            linestyle="--",
            label=f"Mean: {stats[key]['mean']*100:.2f}%",
        )
        axes[i].axhline(
            stats[key]["median"],
            color="g",
            linestyle="-",
            label=f"Median: {stats[key]['median']*100:.2f}%",
        )
        axes[i].axhline(
            stats[key]["min"],
            color="b",
            linestyle=":",
            label=f"Min: {stats[key]['min']*100:.2f}%",
        )
        axes[i].axhline(
            stats[key]["max"],
            color="b",
            linestyle=":",
            label=f"Max: {stats[key]['max']*100:.2f}%",
        )

        # Compute IQR lines
        q25, q75 = np.percentile(data[key], [25, 75])
        axes[i].axhline(
            q25, color="m", linestyle="-.", label=f"25th Percentile: {q25*100:.2f}%"
        )
        axes[i].axhline(
            q75, color="m", linestyle="-.", label=f"75th Percentile: {q75*100:.2f}%"
        )

        # Add legend
        axes[i].legend()

    # make the scale the same for all plots from 0 to 1
    for ax in axes:
        ax.set_ylim(0, 0.4)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


def get_bad_cuts_with_margin(margins, margin_threshold):
    """
    Get the pages with bad cuts based on the margin threshold for each margin.

    Args:
        margins (list): List of dictionaries containing margin information.
        margin_threshold (dict): Dictionary of margin thresholds.

    Returns:
        dict: Dictionary of lists containing page numbers with bad cuts for each margin type.
    """
    bad_cuts = {key: [] for key in margin_threshold.keys()}

    for i, margin in enumerate(margins):
        for key in margin:
            if margin[key] < margin_threshold[key]:
                bad_cuts[key].append(i)

    return bad_cuts


def calculate_margins_to_cut(margins, desired_margins):
    """
    Calculate the margins to cut to achieve desired margins.

    Args:
        margins (dict): Dictionary of current margins.
        desired_margins (dict): Dictionary of desired margins.

    Returns:
        dict: Dictionary of margins to cut as percentages of the original page.
    """

    def solve_margin_to_cut(margin_keys):
        margin_perc = [margins[key] for key in margin_keys]
        desired_margin_perc = [desired_margins[key] for key in margin_keys]

        linear_system_matrix_A = np.array(
            [
                [desired_margin_perc[0] - 1, desired_margin_perc[0]],
                [desired_margin_perc[1], desired_margin_perc[1] - 1],
            ]
        )

        linear_system_matrix_B = np.array(
            [
                desired_margin_perc[0] - margin_perc[0],
                desired_margin_perc[1] - margin_perc[1],
            ]
        )

        return np.linalg.solve(linear_system_matrix_A, linear_system_matrix_B)

    # Check for 'left' and 'right' keys for width margins
    width_keys = ["left", "right"] if "left" in margins else ["inner", "outer"]
    height_keys = ["top", "bottom"]

    x_width = solve_margin_to_cut(width_keys)
    x_height = solve_margin_to_cut(height_keys)

    # Create a dictionary of margins to cut as percentages of the original page
    margins_to_cut = {
        width_keys[0]: x_width[0],
        width_keys[1]: x_width[1],
        "top": x_height[0],
        "bottom": x_height[1],
    }

    return margins_to_cut


def main():
    """
    Main function to run the PDF margin analyzer.
    """
    parser = argparse.ArgumentParser(
        description="Analyze and adjust margins in PDF documents."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--exceptions",
        nargs="+",
        type=int,
        default=[0],
        help="List of pages to exclude (0-based index)",
    )
    parser.add_argument(
        "--inner-outer",
        action="store_true",
        help="Use inner/outer instead of left/right",
    )
    parser.add_argument("--plot", action="store_true", help="Plot margin statistics")
    parser.add_argument(
        "--adjust-to-desired-margins",
        nargs=4,
        type=float,
        metavar=('LEFT/INNER', 'RIGHT/OUTER', 'TOP', 'BOTTOM'),
        help="Adjust margins to desired values as percentages. Use (left, right, top, bottom) or (inner, outer, top, bottom) if --inner-outer is specified",
    )
    args = parser.parse_args()

    document = fitz.open(args.pdf_path)
    margins = calculate_margins(document, args.exceptions, args.inner_outer)
    avg_margins = statistics_margins(margins)
    print_margins(avg_margins, "Margins")

    if args.plot:
        plot_margins(margins)

    if args.adjust_to_desired_margins:
        pessimistic_margins = {
            key: np.percentile(
                [margin[key] for margin in margins if not np.isnan(margin[key])], 25
            )
            for key in margins[0]
        }
        print("\nPessimistic estimate of typical margins:")
        print(pessimistic_margins)

        if args.inner_outer:
            desired_margins = {
                "inner": args.adjust_to_desired_margins[0] / 100,
                "outer": args.adjust_to_desired_margins[1] / 100,
                "top": args.adjust_to_desired_margins[2] / 100,
                "bottom": args.adjust_to_desired_margins[3] / 100,
            }
        else:
            desired_margins = {
                "left": args.adjust_to_desired_margins[0] / 100,
                "right": args.adjust_to_desired_margins[1] / 100,
                "top": args.adjust_to_desired_margins[2] / 100,
                "bottom": args.adjust_to_desired_margins[3] / 100,
            }

        margins_to_cut = calculate_margins_to_cut(pessimistic_margins, desired_margins)
        print("\nMargins to cut:")
        for key, value in margins_to_cut.items():
            print(f"{key:6s}:{value*100:7.1f}%")

        print("\nBad cuts:")
        bad_cuts = get_bad_cuts_with_margin(margins, margins_to_cut)
        for key in bad_cuts:
            print(f"  {key.capitalize()}: {bad_cuts[key]}")

        margins_to_cut = calculate_margins_to_cut(pessimistic_margins, desired_margins)
        print("\nMargins to cut:")
        for key, value in margins_to_cut.items():
            print(f"{key:6s}:{value*100:7.1f}%")

        print("\nBad cuts:")
        bad_cuts = get_bad_cuts_with_margin(margins, margins_to_cut)

        for key in bad_cuts:
            print(f"  {key.capitalize()}: {bad_cuts[key]}")


if __name__ == "__main__":
    main()
