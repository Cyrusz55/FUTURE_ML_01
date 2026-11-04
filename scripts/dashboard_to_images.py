from __future__ import annotations

import io
import re
from pathlib import Path

import pymupdf
from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "docs" / "dashboard"
IMAGE_DIR = ROOT / "docs" / "images"


def slugify(title: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return f"dashboard_{index:02d}_{slug}" if slug else f"dashboard_{index:02d}"


def trim_white_margin(image: Image.Image) -> Image.Image:
    rgb_image = image.convert("RGB")
    background = Image.new("RGB", rgb_image.size, "white")
    difference = ImageChops.difference(rgb_image, background)
    bbox = difference.getbbox()
    if bbox is None:
        return rgb_image

    left, top, right, bottom = bbox
    border = 12
    crop_box = (
        max(0, left - border),
        max(0, top - border),
        min(rgb_image.width, right + border),
        min(rgb_image.height, bottom + border),
    )
    return rgb_image.crop(crop_box)


def page_names(page_count: int) -> list[str]:
    pages_file = DASHBOARD_DIR / "pages.txt"
    if not pages_file.exists():
        return [f"dashboard_{index:02d}" for index in range(1, page_count + 1)]

    titles = [
        line.strip()
        for line in pages_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(titles) != page_count:
        raise ValueError(
            f"pages.txt contains {len(titles)} titles for {page_count} PDF pages"
        )
    return [slugify(title, index) for index, title in enumerate(titles, start=1)]


def find_pdf() -> Path:
    pdfs = sorted(DASHBOARD_DIR.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDF found in {DASHBOARD_DIR}")
    if len(pdfs) > 1:
        raise ValueError(f"Expected one dashboard PDF, found {len(pdfs)}")
    return pdfs[0]


def render_dashboard() -> None:
    pdf_path = find_pdf()
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with pymupdf.open(pdf_path) as document:
        names = page_names(document.page_count)
        for page_number, name in enumerate(names):
            page = document[page_number]
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
            trimmed = trim_white_margin(image)
            output = io.BytesIO()
            trimmed.save(output, format="PNG", optimize=True)
            (IMAGE_DIR / f"{name}.png").write_bytes(output.getvalue())


if __name__ == "__main__":
    render_dashboard()
