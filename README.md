# Horizon Emissive Ores

Makes the mineral pixels in 18 ore textures glow, without lighting the surrounding rock.
An independent Horizon mod, not an official port of Emissive Glowing Ores.

**Requires:** Linux, curl, Git, Python 3.11+, Rust/Cargo with rustup, ImageMagick (`magick`),
and a Horizon client with **mod API 17+** (PR [#2888](https://github.com/horizon-rust/horizon/pull/2888)).
The installer builds the mod locally; the first build can take several minutes.

## Install

Close Horizon, then run:

```sh
curl -fsSL https://raw.githubusercontent.com/ESHAYAT102/horizon-emissive-ores/main/install.sh | sh
```

The script clones/updates the source in `~/.local/share/horizon-emissive-ores/source`,
finds your prepared Horizon textures, builds the masks, installs the `.hmod`,
and enables it. Restart Horizon. Toggle the effect in **Options → Mods → Settings**.
If textures aren't found, append `-s -- --textures /path/to/assets/minecraft/textures/block` after `sh`.

## Uninstall

```sh
curl -fsSL https://raw.githubusercontent.com/ESHAYAT102/horizon-emissive-ores/main/uninstall.sh | sh
```

Restart Horizon afterward. Saved mod settings are kept; worlds and other mods are untouched.

Masks are generated from **your own local vanilla textures**. Do not publish the generated
`.hmod` or `.local/` files. Custom resource packs may need different masks.
