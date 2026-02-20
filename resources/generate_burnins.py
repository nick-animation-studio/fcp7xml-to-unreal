#!/usr/bin/env python3
"""Generate burn-in PNGs by invoking ffmpeg.

Usage examples:
  python scripts/generate_burnins.py --resolution 1920x1080 \
    --outdir tests/resources/burnins_shots --prefix shot --pad 3 --start 1 --end 500 --x 100

  python scripts/generate_burnins.py  --resolution 1920x1080 \
    --outdir tests/resources/burnins_scenes --prefix scene --pad 2 --values 0,99 --x 10

This script calls ffmpeg for each frame. Customize font, fontsize, box padding, and positions.
"""

import argparse
import os
import subprocess


def parse_values(values: str) -> list[int]:
    """Parse a comma-separated list of integers or ranges like 1-5"""
    out = []
    if not values:
        return out
    parts = values.split(",")
    for p in parts:
        p = p.strip()
        if "-" in p:
            a, b = p.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(p))
    return out


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def build_drawtext(
    fontfile: str, text: str, fontsize: int, boxborderw: int, x: int, y: str
) -> str:
    # Make sure fontfile uses forward slashes which ffmpeg accepts on Windows too
    fontfile_safe = fontfile.replace("\\", "/")
    # Escape single quotes in text by replacing with \'
    text_safe = text.replace("'", "\\'")
    text_safe = text_safe.replace(" ", "\\ ")  # Escape spaces too
    # Build filter string
    vf = (
        f"format=rgba,drawtext=fontfile={fontfile_safe}:text={text_safe}:"
        f"fontcolor=white:fontsize={fontsize}:box=1:boxcolor=black@1:boxborderw={boxborderw}:x={x}:y={y},format=rgba"
    )
    return vf


def run_ffmpeg(ffmpeg: str, resolution: str, outfile: str, vf: str) -> None:
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x000000@0x00:s={resolution},format=rgba",
        "-vf",
        vf,
        "-frames:v",
        "1",
        outfile,
    ]
    # Run and capture output for easier debugging
    res = subprocess.run(cmd, capture_output=True, text=True)
    # print(f"ran command: {' '.join(cmd)}")
    if res.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed:\nCMD: {' '.join(cmd)}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        )


def main():
    p = argparse.ArgumentParser(description="Generate burn-in PNG images using ffmpeg")
    p.add_argument(
        "--ffmpeg",
        default=r"C:\ffmpeg\bin\ffmpeg.exe",
        help="Path to ffmpeg executable",
    )
    # p.add_argument('--template', required=True, help='Transparent background PNG to composite onto')
    p.add_argument(
        "--resolution", default="1920x1080", help="Output resolution, e.g. 1920x1080"
    )
    p.add_argument(
        "--outdir", required=True, help="Output directory for generated PNGs"
    )
    p.add_argument("--prefix", required=True, help="Text prefix, e.g. shot or scene")
    p.add_argument("--start", type=int, default=1, help="Start integer (inclusive)")
    p.add_argument("--end", type=int, default=1, help="End integer (inclusive)")
    p.add_argument(
        "--values",
        default=None,
        help='Comma-separated values or ranges, e.g. "1,250,500" or "1-5"',
    )
    p.add_argument("--pad", type=int, default=3, help="Zero-pad width for numbers")
    p.add_argument("--fontsize", type=int, default=20)
    p.add_argument("--boxborderw", type=int, default=8)
    p.add_argument(
        "--fontfile",
        default=r"C:\Windows\Fonts\consola.ttf",
        help="TTF font file to use",
    )
    p.add_argument(
        "--x", type=int, default=100, help="X position for drawtext (pixels)"
    )
    p.add_argument(
        "--y",
        default="(h-text_h)-10",
        help="Y expression for drawtext (ffmpeg expression)",
    )
    p.add_argument("--lower", action="store_true", help="Lowercase the prefix text")
    args = p.parse_args()

    ensure_dir(args.outdir)

    if args.values:
        nums = parse_values(args.values)
    else:
        nums = list(range(args.start, args.end + 1))

    for n in nums:
        num_text = f"{n:0{args.pad}d}"
        prefix = args.prefix.lower() if args.lower else args.prefix
        text = f"{prefix} {num_text}"
        outfile = os.path.join(args.outdir, f"{prefix}_{num_text}.png")
        vf = build_drawtext(
            args.fontfile, text, args.fontsize, args.boxborderw, args.x, args.y
        )
        print(f"Generating {outfile}...")
        run_ffmpeg(args.ffmpeg, args.resolution, outfile, vf)

    print("Done")


if __name__ == "__main__":
    main()
