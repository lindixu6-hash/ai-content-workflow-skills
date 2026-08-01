#!/usr/bin/env python3
"""Validate video streams, dimensions, frame rate, duration, and decoding."""

import argparse
import json
import shutil
import subprocess
from fractions import Fraction
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


def first_stream(data, codec_type):
    return next(
        (item for item in data.get("streams", []) if item.get("codec_type") == codec_type),
        None,
    )


def fps_value(value):
    if not value or value == "0/0":
        return 0.0
    return float(Fraction(value))


def parse_args():
    parser = argparse.ArgumentParser(description="Validate an exported social video.")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--expect-width", type=int)
    parser.add_argument("--expect-height", type=int)
    parser.add_argument("--expect-fps", type=float)
    parser.add_argument("--fps-tolerance", type=float, default=0.05)
    parser.add_argument("--min-duration", type=float, default=0.1)
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument(
        "--skip-full-decode",
        action="store_true",
        help="Skip the slower full FFmpeg decode check.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.video.is_file():
        raise SystemExit(f"Video does not exist: {args.video}")

    data = probe(args.video)
    video = first_stream(data, "video")
    audio = first_stream(data, "audio")
    errors = []

    if not video:
        errors.append("missing video stream")
    else:
        width = int(video.get("width", 0))
        height = int(video.get("height", 0))
        fps = fps_value(video.get("avg_frame_rate") or video.get("r_frame_rate"))

        if args.expect_width is not None and width != args.expect_width:
            errors.append(f"width {width} != {args.expect_width}")
        if args.expect_height is not None and height != args.expect_height:
            errors.append(f"height {height} != {args.expect_height}")
        if (
            args.expect_fps is not None
            and abs(fps - args.expect_fps) > args.fps_tolerance
        ):
            errors.append(f"fps {fps:.3f} != {args.expect_fps:.3f}")

    duration = float(data.get("format", {}).get("duration", 0))
    if duration < args.min_duration:
        errors.append(f"duration {duration:.3f}s < {args.min_duration:.3f}s")
    if args.require_audio and not audio:
        errors.append("missing required audio stream")

    if not args.skip_full_decode:
        ffmpeg = require_tool("ffmpeg")
        decode = subprocess.run(
            [ffmpeg, "-v", "error", "-i", str(args.video), "-f", "null", "-"],
            capture_output=True,
            text=True,
        )
        if decode.returncode != 0 or decode.stderr.strip():
            errors.append(f"full decode failed: {decode.stderr.strip()}")

    result = {
        "path": str(args.video),
        "duration": duration,
        "video": {
            "codec": video.get("codec_name") if video else None,
            "width": int(video.get("width", 0)) if video else None,
            "height": int(video.get("height", 0)) if video else None,
            "fps": fps_value(video.get("avg_frame_rate")) if video else None,
        },
        "audio": {
            "present": bool(audio),
            "codec": audio.get("codec_name") if audio else None,
        },
        "full_decode": not args.skip_full_decode,
        "ok": not errors,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
