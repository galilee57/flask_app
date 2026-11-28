"""Build static responsive WebP images; originals and Markdown stay untouched.

Run with Python 3.11+ after installing requirements-images.txt.
"""
import json
from pathlib import Path

from PIL import Image, ImageOps


IMAGE_DIR = Path(__file__).resolve().parents[1] / "app/realizations/static/images"
WIDTHS = (320, 640, 960, 1440)


def build_images(image_dir=IMAGE_DIR):
    output_dir = image_dir / "responsive"
    output_dir.mkdir(exist_ok=True)
    manifest = {}
    original_bytes = 0
    card_bytes = 0
    for source in sorted(image_dir.rglob("*")):
        if (not source.is_file() or output_dir in source.parents
                or source.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}):
            continue
        with Image.open(source) as original:
            # Do not replace animated assets with their first frame.
            if getattr(original, "is_animated", False):
                continue
            image = ImageOps.exif_transpose(original)
            image = image.convert("RGBA" if "A" in image.getbands() or "transparency" in image.info else "RGB")
            relative_path = source.relative_to(image_dir)
            relative = relative_path.as_posix()
            # Source assets live under imported/<project>/ or generated/<project>/.
            # Keep the project folder and source name so variants are easy to find.
            project_dir = relative_path.parent.name
            variants = []
            for width in sorted({min(width, image.width) for width in WIDTHS}):
                height = max(1, round(image.height * width / image.width))
                target = output_dir / project_dir / f"{source.stem}-{width}.webp"
                target.parent.mkdir(parents=True, exist_ok=True)
                resized = image.resize((width, height), Image.Resampling.LANCZOS)
                resized.save(target, "WEBP", quality=78 if width <= 960 else 82,
                             method=6, icc_profile=image.info.get("icc_profile", b""))
                variants.append({"file": target.relative_to(image_dir).as_posix(),
                                 "width": width, "height": height})
            manifest[relative] = {"width": image.width, "height": image.height,
                                  "variants": variants}
            original_bytes += source.stat().st_size
            card = next((v for v in variants if v["width"] >= 640), variants[-1])
            card_bytes += (image_dir / card["file"]).stat().st_size
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{len(manifest)} images: originals {original_bytes:,} bytes; "
          f"640px variants {card_bytes:,} bytes "
          f"({100 * (1 - card_bytes / original_bytes):.1f}% smaller).")


if __name__ == "__main__":
    build_images()
