#!/usr/bin/env python3
"""Generate the PixMint Games landing image assets from the shared brand pack.

Reads (never writes) the brand pack in ``../PixMintGamesMobile/docs`` and writes
only into ``site/assets/``. Re-running the script produces byte-identical files
(PNG/ICO output is deterministic), so it is safe to run in CI.

The Open Graph card is composed from the canonical ``wordmark-1024-wide.svg``
vector, rasterised in-process (quadratic paths + even-odd fill), so no cairosvg,
font, or network dependency is required. If the vector render ever fails, the
script falls back to centring the Play feature graphic on the ink canvas.

Usage:
    python tool/generate_assets.py            # write assets
    python tool/generate_assets.py --check    # verify assets are current
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "site" / "assets"
BRAND_DOCS = ROOT.parent / "PixMintGamesMobile" / "docs"

INK = (30, 27, 46)  # #1E1B2E
ORANGE = (242, 84, 27)  # #F2541B

INPUTS = {
    "app_icon": BRAND_DOCS / "brand" / "app-icon-master-1024.png",
    "wordmark_svg": BRAND_DOCS / "brand" / "wordmark-1024-wide.svg",
    "splash": BRAND_DOCS / "brand" / "splash-artwork-1152.png",
    "feature_graphic": BRAND_DOCS / "store" / "feature-graphic-1024x500.jpg",
    "play_icon": BRAND_DOCS / "store" / "play-store-icon-512.png",
}

# Favicon legibility: the master icon keeps ~27% padding on each side, which
# leaves the P mark only ~59% of the tile height. Trimming 8% per side keeps the
# brand's breathing room while making the mark read at 32 px.
FAVICON_CROP = 0.08

OG_SIZE = (1200, 630)
OG_WORDMARK_WIDTH = 880  # ink width, centred; ~900 px per the brief
SUPERSAMPLE = 4  # vector rasterisation oversampling before LANCZOS downscale
CURVE_STEPS = 24  # quadratic flattening segments

_NUMBER = r"-?(?:\d+\.\d+|\.\d+|\d+)"
_TOKEN = re.compile(r"[A-Za-z]|" + _NUMBER)


class AssetError(RuntimeError):
    pass


# --------------------------------------------------------------------------- #
# SVG path parsing / rasterisation (quadratic + cubic, absolute + relative)
# --------------------------------------------------------------------------- #
def _flatten_quad(p0, p1, p2, steps=CURVE_STEPS):
    pts = []
    for i in range(1, steps + 1):
        t = i / steps
        u = 1.0 - t
        pts.append(
            (
                u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
            )
        )
    return pts


def _flatten_cubic(p0, p1, p2, p3, steps=CURVE_STEPS):
    pts = []
    for i in range(1, steps + 1):
        t = i / steps
        u = 1.0 - t
        pts.append(
            (
                u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
            )
        )
    return pts


def parse_svg_path(d: str) -> list[list[tuple[float, float]]]:
    """Flatten an SVG path into closed polygons (subpaths)."""
    toks = _TOKEN.findall(d)
    i = 0
    cmd = ""
    x = y = 0.0
    start = (0.0, 0.0)
    subpaths: list[list[tuple[float, float]]] = []
    cur: list[tuple[float, float]] = []
    last_quad: tuple[float, float] | None = None  # for T
    last_cubic: tuple[float, float] | None = None  # for S

    def take(n: int) -> list[float]:
        nonlocal i
        vals = [float(v) for v in toks[i : i + n]]
        if len(vals) != n:
            raise AssetError("truncated SVG path data")
        i += n
        return vals

    while i < len(toks):
        tok = toks[i]
        if tok.isalpha():
            cmd = tok
            i += 1
            if cmd in "Zz":
                if cur:
                    subpaths.append(cur)
                    cur = []
                x, y = start
            continue
        if not cmd:
            raise AssetError("SVG path data does not start with a command")
        rel = cmd.islower()
        op = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)

        if op == "M":
            nx, ny = take(2)
            x, y = nx + ox, ny + oy
            if cur:
                subpaths.append(cur)
            cur = [(x, y)]
            start = (x, y)
            cmd = "l" if rel else "L"  # implicit lineto after moveto
            last_quad = last_cubic = None
        elif op == "L":
            nx, ny = take(2)
            x, y = nx + ox, ny + oy
            cur.append((x, y))
            last_quad = last_cubic = None
        elif op == "H":
            (nx,) = take(1)
            x = nx + ox
            cur.append((x, y))
            last_quad = last_cubic = None
        elif op == "V":
            (ny,) = take(1)
            y = ny + oy
            cur.append((x, y))
            last_quad = last_cubic = None
        elif op == "Q":
            x1, y1, nx, ny = take(4)
            p0 = (x, y)
            p1 = (x1 + ox, y1 + oy)
            p2 = (nx + ox, ny + oy)
            cur.extend(_flatten_quad(p0, p1, p2))
            x, y = p2
            last_quad, last_cubic = p1, None
        elif op == "T":
            nx, ny = take(2)
            p0 = (x, y)
            p1 = (
                (2 * x - last_quad[0], 2 * y - last_quad[1])
                if last_quad
                else p0
            )
            p2 = (nx + ox, ny + oy)
            cur.extend(_flatten_quad(p0, p1, p2))
            x, y = p2
            last_quad, last_cubic = p1, None
        elif op == "C":
            x1, y1, x2, y2, nx, ny = take(6)
            p0 = (x, y)
            p1 = (x1 + ox, y1 + oy)
            p2 = (x2 + ox, y2 + oy)
            p3 = (nx + ox, ny + oy)
            cur.extend(_flatten_cubic(p0, p1, p2, p3))
            x, y = p3
            last_cubic, last_quad = p2, None
        elif op == "S":
            x2, y2, nx, ny = take(4)
            p0 = (x, y)
            p1 = (
                (2 * x - last_cubic[0], 2 * y - last_cubic[1])
                if last_cubic
                else p0
            )
            p2 = (x2 + ox, y2 + oy)
            p3 = (nx + ox, ny + oy)
            cur.extend(_flatten_cubic(p0, p1, p2, p3))
            x, y = p3
            last_cubic, last_quad = p2, None
        else:
            raise AssetError(f"unsupported SVG path command: {cmd}")

    if cur:
        subpaths.append(cur)
    if not subpaths:
        raise AssetError("SVG path produced no subpaths")
    return subpaths


def _bounds(subpaths):
    xs = [p[0] for sp in subpaths for p in sp]
    ys = [p[1] for sp in subpaths for p in sp]
    return min(xs), min(ys), max(xs), max(ys)


def render_wordmark(target_width: int) -> Image.Image:
    """Rasterise the canonical wordmark SVG into an RGBA glyph image.

    Subpaths are composited with even-odd (XOR) fill so glyph counters such as
    the P bowl stay open.
    """
    svg = INPUTS["wordmark_svg"].read_text(encoding="utf-8")
    match = re.search(r'<path[^>]*\sd="([^"]+)"', svg)
    if not match:
        raise AssetError("wordmark-1024-wide.svg has no single path to render")
    subpaths = parse_svg_path(match.group(1))

    minx, miny, maxx, maxy = _bounds(subpaths)
    aspect = (maxy - miny) / (maxx - minx)
    big_w = target_width * SUPERSAMPLE
    big_h = max(1, round(big_w * aspect))
    scale = big_w / (maxx - minx)

    acc: Image.Image | None = None
    for poly in subpaths:
        plane = Image.new("1", (big_w, big_h), 0)
        ImageDraw.Draw(plane).polygon(
            [((px - minx) * scale, (py - miny) * scale) for px, py in poly], fill=1
        )
        acc = plane if acc is None else ImageChops.logical_xor(acc, plane)
    assert acc is not None

    out_h = max(1, round(target_width * aspect))
    mask = acc.convert("L").resize((target_width, out_h), Image.LANCZOS)
    glyphs = Image.new("RGBA", (target_width, out_h), ORANGE + (0,))
    glyphs.putalpha(mask)
    return glyphs


# --------------------------------------------------------------------------- #
# IO helpers
# --------------------------------------------------------------------------- #
def _guard(path: Path) -> Path:
    resolved = path.resolve()
    if OUT_DIR.resolve() not in resolved.parents:
        raise AssetError(f"refusing to write outside site/assets: {resolved}")
    return resolved


def _png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _ico_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="ICO", sizes=[(32, 32)])
    return buf.getvalue()


def _write(name: str, data: bytes) -> None:
    path = _guard(OUT_DIR / name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


# --------------------------------------------------------------------------- #
# Asset builders
# --------------------------------------------------------------------------- #
def load_sources() -> None:
    missing = [str(p) for p in INPUTS.values() if not p.is_file()]
    if missing:
        raise AssetError("missing brand inputs:\n  " + "\n  ".join(missing))


def build_favicon() -> tuple[Image.Image, bytes]:
    master = Image.open(INPUTS["app_icon"]).convert("RGB")
    w, h = master.size
    inset = round(min(w, h) * FAVICON_CROP)
    cropped = master.crop((inset, inset, w - inset, h - inset))
    icon = cropped.resize((32, 32), Image.LANCZOS)
    return icon, _png_bytes(icon)


def build_apple_touch() -> bytes:
    master = Image.open(INPUTS["app_icon"]).convert("RGBA")
    scaled = master.resize((180, 180), Image.LANCZOS)
    canvas = Image.new("RGB", (180, 180), ORANGE)  # opaque: iOS paints black behind alpha
    canvas.paste(scaled, (0, 0), scaled)
    return _png_bytes(canvas)


def build_icon_512() -> bytes:
    master = Image.open(INPUTS["app_icon"]).convert("RGB")
    return _png_bytes(master.resize((512, 512), Image.LANCZOS))


def build_og_image() -> tuple[bytes, str]:
    width, height = OG_SIZE
    canvas = Image.new("RGB", (width, height), INK)
    try:
        hi_res = render_wordmark(OG_WORDMARK_WIDTH * 2)
        target_h = max(1, round(hi_res.height * OG_WORDMARK_WIDTH / hi_res.width))
        glyphs = hi_res.resize((OG_WORDMARK_WIDTH, target_h), Image.LANCZOS)
        left = (width - glyphs.width) // 2
        top = (height - glyphs.height) // 2
        canvas.paste(glyphs, (left, top), glyphs)
        path = "wordmark-vector"
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"  ! wordmark render failed ({exc}); using feature graphic", file=sys.stderr)
        feature = Image.open(INPUTS["feature_graphic"]).convert("RGB")
        target_w = width
        target_h = round(feature.height * target_w / feature.width)
        if target_h > height:
            target_h = height
            target_w = round(feature.width * target_h / feature.height)
        feature = feature.resize((target_w, target_h), Image.LANCZOS)
        canvas.paste(feature, ((width - target_w) // 2, (height - target_h) // 2))
        path = "feature-graphic-fallback"
    return _png_bytes(canvas), path


def build_all() -> dict[str, bytes]:
    favicon, favicon_png = build_favicon()
    og_bytes, og_path = build_og_image()
    print(f"  og-image composition: {og_path}")
    if len(og_bytes) > 200_000:
        print(
            f"  ! og-image is {len(og_bytes) / 1024:.1f} KB (over the 200 KB target)",
            file=sys.stderr,
        )
    return {
        "favicon-32.png": favicon_png,
        "apple-touch-icon.png": build_apple_touch(),
        "icon-512.png": build_icon_512(),
        "og-image.png": og_bytes,
        "favicon.ico": _ico_bytes(favicon),
        "wordmark.svg": INPUTS["wordmark_svg"].read_bytes(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify without writing")
    args = parser.parse_args(argv)

    load_sources()
    assets = build_all()

    stale = []
    for name, data in assets.items():
        path = _guard(OUT_DIR / name)
        current = path.read_bytes() if path.is_file() else None
        if current != data:
            stale.append(name)

    if args.check:
        if stale:
            print("stale assets: " + ", ".join(stale))
            return 1
        print(f"all {len(assets)} assets current")
        return 0

    for name, data in assets.items():
        _write(name, data)
    total = sum(len(d) for d in assets.values())
    print(f"wrote {len(assets)} files to site/assets ({total / 1024:.1f} KB)")
    for name, data in assets.items():
        print(f"  {name:22s} {len(data):>8,} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
