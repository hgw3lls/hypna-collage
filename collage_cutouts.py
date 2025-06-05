# -*- coding: utf-8 -*-
"""Generate torn paper-style cutouts from images in a folder.

Usage:
    python collage_cutouts.py <input_folder> <output_folder>

This script scans the input folder for common image files, finds salient
areas of each image, and exports a PNG with an irregular mask to resemble
a torn paper edge. The output PNG retains transparency around the torn
mask so it can be composed later into a collage.
"""

import sys
from pathlib import Path
import cv2
import numpy as np


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}


def compute_saliency(image: np.ndarray) -> np.ndarray:
    """Return a normalized saliency map for the given BGR image."""
    saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
    ok, map = saliency.computeSaliency(image)
    if not ok:
        raise RuntimeError("Failed to compute saliency")
    map = (map * 255).astype("uint8")
    return map


def torn_mask_from_saliency(saliency_map: np.ndarray) -> np.ndarray:
    """Generate a binary mask with irregular torn edges based on saliency."""
    # Threshold using Otsu to pick salient region
    _, thresh = cv2.threshold(saliency_map, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Dilate then erode with irregular kernels to create torn look
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    mask = cv2.dilate(thresh, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)
    # Add small random noise to edge to mimic tear
    noise = np.random.randint(0, 2, mask.shape, dtype="uint8") * 255
    mask = cv2.bitwise_or(mask, cv2.erode(noise, None))
    mask = cv2.GaussianBlur(mask, (11, 11), 0)
    return mask


def process_image(path: Path, out_folder: Path) -> None:
    image = cv2.imread(str(path))
    if image is None:
        print(f"Warning: could not read {path}")
        return
    saliency_map = compute_saliency(image)
    mask = torn_mask_from_saliency(saliency_map)

    # Create 4-channel output with alpha
    bgr = image.copy()
    alpha = mask
    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = alpha

    out_path = out_folder / (path.stem + "_cutout.png")
    cv2.imwrite(str(out_path), rgba)
    print(f"Saved {out_path}")


def main(input_dir: str, output_dir: str) -> None:
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for file in in_path.iterdir():
        if file.suffix.lower() in SUPPORTED_EXTS:
            process_image(file, out_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python collage_cutouts.py <input_folder> <output_folder>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
