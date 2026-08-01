#!/usr/bin/env python3
"""Overlay an animation video on a talking-head video while preserving audio."""

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def require_tool(name):
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Missing required executable: {name}")
    return path


def probe(path):
    ffprobe = require_tool("ffprobe")
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def stream(data, codec_type):
    return next(
        (item for item in data.get("streams", []) if item.get("codec_type") == codec_type),
        None,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Overlay transparent HTML animation output on a talking-head video."
    )
    parser.add_argument("--base", required=True, type=Path, help="Talking-head video.")
    parser.add_argument("--overlay", required=True, type=Path, help="Overlay video.")
    parser.add_argument("--output", required=True, type=Path, help="Output MP4.")
    parser.add_argument("--x", type=int, default=0, help="Overlay x position.")
    parser.add_argument("--y", type=int, default=0, help="Overlay y position.")
    parser.add_argument("--crf", type=int, default=18, help="H.264 CRF.")
    parser.add_argument("--preset", default="medium", help="H.264 preset.")
    parser.add_argument(
        "--audio-codec",
        choices=("copy", "aac"),
        default="copy",
        help="Copy original audio or encode AAC.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace output.")
    return parser.parse_args()


def main():
    args = parse_args()
    ffmpeg = require_tool("ffmpeg")

    for path in (args.base, args.overlay):
        if not path.is_file():
            raise SystemExit(f"Input does not exist: {path}")

    if args.output.exists() and not args.overwrite:
        raise SystemExit(f"Output exists. Pass --overwrite: {args.output}")

    base_info = probe(args.base)
    overlay_info = probe(args.overlay)
    base_video = stream(base_info, "video")
    overlay_video = stream(overlay_info, "video")
    base_audio = stream(base_info, "audio")

    if not base_video:
        raise SystemExit("Base input has no video stream.")
    if not overlay_video:
        raise SystemExit("Overlay input has no video stream.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    filter_complex = (
        "[1:v]format=rgba[overlay];"
        f"[0:v][overlay]overlay=x={args.x}:y={args.y}:"
        "format=auto:eof_action=pass:shortest=0[outv]"
    )

    command = [
        ffmpeg,
        "-y" if args.overwrite else "-n",
        "-i",
        str(args.base),
        "-i",
        str(args.overlay),
        "-filter_complex",
        filter_complex,
        "-map",
        "[outv]",
    ]

    if base_audio:
        command.extend(["-map", "0:a:0"])

    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            args.preset,
            "-crf",
            str(args.crf),
            "-pix_fmt",
            "yuv420p",
        ]
    )

    if base_audio:
        if args.audio_codec == "copy":
            command.extend(["-c:a", "copy"])
        else:
            command.extend(["-c:a", "aac", "-b:a", "192k"])

    command.extend(["-movflags", "+faststart", str(args.output)])

    print("Running:")
    print(" ".join(command))
    subprocess.run(command, check=True)

    output_info = probe(args.output)
    output_video = stream(output_info, "video")
    output_audio = stream(output_info, "audio")
    if not output_video:
        raise SystemExit("Output validation failed: no video stream.")
    if base_audio and not output_audio:
        raise SystemExit("Output validation failed: base audio was lost.")

    duration = float(output_info.get("format", {}).get("duration", 0))
    print(
        f"OK output={args.output} "
        f"size={output_video.get('width')}x{output_video.get('height')} "
        f"duration={duration:.3f}s audio={'yes' if output_audio else 'no'}"
    )


if __name__ == "__main__":
    main()
