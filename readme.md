# Hypna Collage

This repository contains a tool for generating torn-paper style cutouts from a
folder of images. The resulting PNG files have transparency around the torn
edges and can be used to compose a collage.

## Requirements
- Python 3
- `opencv-contrib-python-headless` and `numpy`

Install dependencies with:

```bash
pip install opencv-contrib-python-headless numpy
```

## Usage

```bash
python collage_cutouts.py <input_folder> <output_folder>
```

The script scans `<input_folder>` for common image formats (JPEG, PNG, BMP, GIF)
and saves new files with `_cutout.png` appended in `<output_folder>`.

Example:

```bash
python collage_cutouts.py images cutouts
```

This will create `cutouts/your_image_cutout.png` for each supported image in the
`images` directory.
