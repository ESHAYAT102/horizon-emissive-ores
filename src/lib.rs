use horizon_mod_sdk::{Mod, Registration, game, render};

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
    applied_dimension: Option<String>,
}

impl Mod for Ores {
    fn init() -> Result<(Self, Registration), String> {
        let ores = Self {
            applied_dimension: None,
        };
        Ok((ores, Registration::new().on_tick()))
    }

    fn tick(&mut self, _tick: u64) {
        let Some(player) = game::get_player() else {
            if self.applied_dimension.take().is_some() {
                let _ = render::set_emissive_materials(&[], false);
            }
            return;
        };
        if self.applied_dimension.as_deref() != Some(&player.dimension) {
            render::set_emissive_materials(&materials(), false)
                .expect("Could not apply emissive ore materials");
            self.applied_dimension = Some(player.dimension);
        }
    }
}

horizon_mod_sdk::export_mod!(Ores);
