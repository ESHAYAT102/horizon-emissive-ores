#!/bin/sh
set -eu
repo=https://github.com/ESHAYAT102/horizon-emissive-ores.git
root=${HORIZON_EMISSIVE_ORES_SOURCE:-${XDG_DATA_HOME:-$HOME/.local/share}/horizon-emissive-ores/source}
for tool in git python3; do
    command -v "$tool" >/dev/null 2>&1 || { echo "Missing $tool. Install it first." >&2; exit 1; }
done
if [ -e "$root" ]; then
    [ -d "$root/.git" ] || { echo "Not a Git checkout: $root" >&2; exit 1; }
    [ "$(git -C "$root" remote get-url origin)" = "$repo" ] || { echo "Unexpected repository at $root" >&2; exit 1; }
    git -C "$root" diff --quiet
    git -C "$root" diff --cached --quiet
    git -C "$root" pull --ff-only origin main
else
    mkdir -p "$(dirname -- "$root")"
    git clone --depth 1 --branch main "$repo" "$root"
fi
exec python3 "$root/tools/manage.py" uninstall "$@"
