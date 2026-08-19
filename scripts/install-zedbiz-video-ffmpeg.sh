#!/usr/bin/env bash
set -euo pipefail

target="${1:-/usr/local/bin/ffmpeg}"
version="N-126217-ge1e325235e-20260819"
archive="ffmpeg-N-126217-ge1e325235e-linux64-gpl.tar.xz"
url="https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-08-19-19-21/${archive}"
archive_sha256="c3df9379d32a16f6923681411c97880ee8d45b0bae03a55a6fc8262f2f653ba6"

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

curl -fsSL "$url" -o "$workdir/$archive"
echo "$archive_sha256  $workdir/$archive" | sha256sum -c -
tar -xJf "$workdir/$archive" -C "$workdir"
candidate="$(find "$workdir" -type f -path '*/bin/ffmpeg' -print -quit)"

if [[ -z "$candidate" ]]; then
  echo "FFmpeg binary was not found in the verified archive." >&2
  exit 1
fi

"$candidate" -hide_banner -filters 2>/dev/null | grep -q ' drawtext '
"$candidate" -nostdin -hide_banner -loglevel error \
  -f lavfi -i 'color=c=blue:s=320x180:d=0.2' \
  -vf "drawtext=text='ZedBiz':fontcolor=white:fontsize=24:x=10:y=10" \
  -c:v libx264 -f null -

install -d "$(dirname "$target")"
if [[ -e "$target" ]]; then
  cp "$target" "${target}.bak-$(date -u +%Y%m%dT%H%M%SZ)"
fi
install -m 0755 "$candidate" "$target"

"$target" -hide_banner -filters 2>/dev/null | grep -q ' drawtext '
echo "Installed FFmpeg $version with drawtext at $target"
