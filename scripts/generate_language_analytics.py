#!/usr/bin/env python3
"""Generate the dynamic GitHub language pie chart as Mermaid in README.md."""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "docs", "data", "stats.json")
README = os.path.join(ROOT, "README.md")

START = "<!-- LANGUAGE_ANALYTICS_START -->"
END = "<!-- LANGUAGE_ANALYTICS_END -->"
LEGACY = re.compile(
    r'\n<div align="center">\n<img src="assets/language-analytics\.(?:png|svg)"[^>]*>\n</div>\n',
    re.DOTALL,
)


def main():
    with open(DATA, encoding="utf-8") as handle:
        data = json.load(handle)

    languages = [
        item for item in data.get("languages", [])
        if item.get("name") and item.get("bytes", 0) > 0
    ]
    languages.sort(key=lambda item: item.get("bytes", 0), reverse=True)

    total = sum(item["bytes"] for item in languages) or 1
    top = languages[:6]
    other_bytes = total - sum(item["bytes"] for item in top)

    lines = [
        START,
        "### Language Distribution",
        "",
        "```mermaid",
        "pie showData",
        "    title GitHub Language Distribution",
    ]

    for item in top:
        share = item["bytes"] / total * 100
        lines.append(f'    "{item["name"]}" : {share:.2f}')

    if other_bytes > 0:
        lines.append(f'    "Other" : {other_bytes / total * 100:.2f}')

    lines.extend([
        "```",
        "",
        "_Generated from live GitHub repository language byte data by Python._",
        END,
    ])
    block = "\n".join(lines)

    with open(README, encoding="utf-8") as handle:
        readme = handle.read()

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if pattern.search(readme):
        readme = pattern.sub(block, readme, count=1)
    else:
        marker = '<h2 align="center">Language Analytics</h2>'
        if marker not in readme:
            raise RuntimeError("Language Analytics heading not found in README.md")
        readme = readme.replace(marker, marker + "\n\n" + block, 1)

    # Remove the old static PNG/SVG chart completely.
    readme = LEGACY.sub("\n", readme)

    with open(README, "w", encoding="utf-8") as handle:
        handle.write(readme)


if __name__ == "__main__":
    main()
