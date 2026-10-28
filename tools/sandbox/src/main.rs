use horizon_mods::{Mods, Snapshot, Status};
use std::path::PathBuf;

fn main() {
    let package = PathBuf::from(std::env::args().nth(1).expect("pass .hmod path"));
    let scratch = std::env::temp_dir().join(format!("emissive-ores-check-{}", std::process::id()));
    std::fs::create_dir(&scratch).unwrap();
    let path = scratch.join("ores.hmod");
    std::fs::copy(package, &path).unwrap();
    // A legacy OFF preference must not override the single Mods-list toggle.
    let legacy = scratch.join(".horizon-mod-data/horizon_emissive_ores");
    std::fs::create_dir_all(&legacy).unwrap();
    std::fs::write(legacy.join("enabled"), b"false").unwrap();
    let load = |enabled| Mods::load(std::slice::from_ref(&path), |_| enabled, |_| false);
    let mut mods = load(false);
    assert_eq!(mods.entries()[0].status, Status::Off);
    assert_eq!(mods.emissive_materials().count(), 0);
    mods = load(true);
    assert_eq!(mods.entries()[0].status, Status::Running);
    assert!(!mods.entries()[0].has_ui_settings());
    assert!(mods.settings_widgets(0).is_empty());
    let mut snapshot = Snapshot::default();
    snapshot.player = Some(horizon_mods::testing::default_player());
    mods.set_snapshot(snapshot.clone());
    mods.tick(1);
    assert_eq!(mods.emissive_materials().count(), 18);
    assert!(!mods.emissive_suffixes());
    assert_eq!(mods.colored_lights().count(), 0);
    assert_eq!(mods.post_effects().count(), 0);
    snapshot.player.as_mut().unwrap().dimension = "minecraft:the_nether".into();
    mods.set_snapshot(snapshot.clone());
    mods.tick(2);
    assert_eq!(mods.emissive_materials().count(), 18);
    mods = load(false);
    assert_eq!(mods.emissive_materials().count(), 0);
    mods = load(true);
    mods.set_snapshot(snapshot);
    mods.tick(3);
    assert_eq!(mods.emissive_materials().count(), 18);
    mods.set_snapshot(Snapshot::default());
    mods.tick(4);
    assert_eq!(mods.emissive_materials().count(), 0);
    assert_eq!(mods.entries()[0].status, Status::Running);
    drop(mods);
    std::fs::remove_dir_all(scratch).unwrap();
    println!(
        "PASS: one toggle, no Settings page, legacy preference ignored, dimension/world-exit cleanup"
    );
}
