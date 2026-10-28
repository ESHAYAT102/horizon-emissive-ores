# Horizon Emissive Ores

Makes the mineral pixels in 18 ore textures glow, without lighting the surrounding rock.
An independent Horizon mod, not an official port of Emissive Glowing Ores.

**Requires:** Linux, Python 3.11+, Rust/Cargo with rustup, ImageMagick (`magick`),
and a Horizon client with **mod API 17+** (PR [#2888](https://github.com/horizon-rust/horizon/pull/2888)).
The installer builds the mod locally; the first build can take several minutes.

## Install

Close Horizon, then run:

```sh
git clone https://github.com/ESHAYAT102/horizon-emissive-ores.git
cd horizon-emissive-ores
./install.sh
```

The script finds your prepared Horizon textures, builds the masks, installs the `.hmod`,
and enables it. Restart Horizon. Toggle the effect in **Options → Mods → Settings**.
If textures aren't found, use `./install.sh --textures /path/to/assets/minecraft/textures/block`.

## Uninstall

```sh
./uninstall.sh
```

Restart Horizon afterward. Saved mod settings are kept; worlds and other mods are untouched.

Masks are generated from **your own local vanilla textures**. Do not publish the generated
`.hmod` or `.local/` files. Custom resource packs may need different masks.
