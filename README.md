# Horizon Emissive Ores

Makes the mineral pixels in 18 ore textures glow, without lighting the surrounding rock.
An independent Horizon mod, not an official port of Emissive Glowing Ores.

**Requires:** a Horizon client with **mod API 17+**
(PR [#2888](https://github.com/horizon-rust/horizon/pull/2888)).

## Download and install

1. Download [`horizon_emissive_ores.hmod`](https://github.com/ESHAYAT102/horizon-emissive-ores/releases/latest/download/horizon_emissive_ores.hmod) from [Releases](https://github.com/ESHAYAT102/horizon-emissive-ores/releases).
2. Close Horizon and copy the file into your game home's **`horizon-mods`** folder.
   On Linux, the default is `~/.local/share/horizon/horizon-mods/`. Create it if needed.
   For a custom instance, use its game folder instead.
3. Start Horizon, open **Options → Mods**, enable **Horizon Emissive Ores**,
   then open its **Settings** and turn **Emissive ores: ON**.

No Rust or build tools are needed for the download. The package targets vanilla **26.3** textures.
To remove it manually, close Horizon and delete the `.hmod` file.

## Install from source (Linux)

Requires curl, Git, Python 3.11+, Rust/Cargo with rustup, and ImageMagick (`magick`).
This builds masks from your own prepared textures; the first build can take several minutes.

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

Source builds generate masks from **your own local vanilla textures**. Custom resource packs
may need different masks. Generated files stay outside Git. The MIT license covers the original
mod code, not the Minecraft artwork used to derive the prebuilt masks. Not affiliated with Mojang.
