use horizon_mod_sdk::{Mod, Registration, game, render, storage, ui};

const ORES: &[&str] = &[
    "coal", "iron", "copper", "gold", "redstone", "emerald", "lapis", "diamond",
];

fn materials() -> Vec<render::EmissiveMaterial> {
    let mut result = Vec::new();
    for ore in ORES {
        for prefix in ["", "deepslate_"] {
            result.push(render::EmissiveMaterial {
                base: format!("minecraft:block/{prefix}{ore}_ore"),
                overlay: format!("horizon_emissive_ores:emissive/{prefix}{ore}_ore"),
            });
        }
    }
    for base in ["nether_gold_ore", "nether_quartz_ore"] {
        result.push(render::EmissiveMaterial {
            base: format!("minecraft:block/{base}"),
            overlay: format!("horizon_emissive_ores:emissive/{base}"),
        });
    }
    result
}

struct Ores {
    enabled: bool,
    applied_dimension: Option<String>,
}

impl Ores {
    fn settings(&self) {
        ui::set_settings(&[ui::Widget::Button(ui::ButtonWidget {
            id: 1,
            label: format!("Emissive ores: {}", if self.enabled { "ON" } else { "OFF" }),
        })]);
    }

    fn toggle(&mut self) -> Result<(), String> {
        let enabled = !self.enabled;
        // Persist first: a failed save must not silently change the active setting.
        storage::set("enabled", if enabled { b"true" } else { b"false" })?;
        self.enabled = enabled;
        self.applied_dimension = None;
        if !enabled {
            render::set_emissive_materials(&[], false)?;
        }
        self.settings();
        Ok(())
    }
}

impl Mod for Ores {
    fn init() -> Result<(Self, Registration), String> {
        let ores = Self {
            enabled: storage::get("enabled").as_deref() == Some(b"true"),
            applied_dimension: None,
        };
        ores.settings();
        Ok((ores, Registration::new().on_tick()))
    }

    fn tick(&mut self, _tick: u64) {
        let Some(player) = game::get_player() else {
            if self.applied_dimension.take().is_some() {
                let _ = render::set_emissive_materials(&[], false);
            }
            return;
        };
        if self.enabled && self.applied_dimension.as_deref() != Some(&player.dimension) {
            match render::set_emissive_materials(&materials(), false) {
                Ok(()) => self.applied_dimension = Some(player.dimension),
                Err(error) => {
                    self.enabled = false;
                    horizon_mod_sdk::log::write(
                        horizon_mod_sdk::log::Level::Error,
                        &format!("Emissive ores disabled: {error}"),
                    );
                    self.settings();
                }
            }
        }
    }

    fn ui_select(&mut self, id: u32, _row: u32) {
        if id == 1
            && let Err(error) = self.toggle()
        {
            horizon_mod_sdk::log::write(
                horizon_mod_sdk::log::Level::Error,
                &format!("Could not change emissive ores: {error}"),
            );
        }
    }

    fn ui_settings_opened(&mut self) {
        self.settings();
    }
}

horizon_mod_sdk::export_mod!(Ores);
