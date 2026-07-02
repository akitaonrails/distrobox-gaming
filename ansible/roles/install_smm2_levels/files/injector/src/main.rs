//! smm2-inject — register downloaded SMM2 courses in a save file.
//!
//! Takes a directory of rank-ordered course files (001.bcd + optional
//! 001.jpg thumbnails, as produced by fetch-popular.py) and adds them to
//! an SMM2 save via smmdb-lib, which handles course/thumbnail encryption
//! and save.dat slot registration. Slots 0-59 are "My Courses" (full
//! editor access in Coursebot).
//!
//! Usage: smm2-inject <save_dir> <courses_dir> [start_slot]

use anyhow::{bail, Context, Result};
use smmdb_lib::{course2::Course2, thumbnail2::Thumbnail2, save::Save};
use std::fs;
use std::path::PathBuf;

#[async_std::main]
async fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 3 {
        bail!("usage: smm2-inject <save_dir> <courses_dir> [start_slot]");
    }
    let save_dir = PathBuf::from(&args[1]);
    let courses_dir = PathBuf::from(&args[2]);
    let start_slot: u8 = args.get(3).map(|s| s.parse()).transpose()?.unwrap_or(0);

    if !save_dir.join("save.dat").is_file() {
        bail!(
            "no save.dat in {} — launch SMM2 once so the game creates its save",
            save_dir.display()
        );
    }

    let mut bcds: Vec<PathBuf> = fs::read_dir(&courses_dir)?
        .filter_map(|e| e.ok().map(|e| e.path()))
        .filter(|p| p.extension().map(|e| e == "bcd").unwrap_or(false))
        .collect();
    bcds.sort();
    if bcds.is_empty() {
        bail!("no .bcd files in {}", courses_dir.display());
    }

    let mut save = Save::new(save_dir.clone())
        .await
        .context("failed to parse save (corrupted save.dat?)")?;

    let mut slot = start_slot;
    let mut added = 0u32;
    for bcd in &bcds {
        if slot >= 60 {
            eprintln!("stopping: My Courses slots exhausted (0-59)");
            break;
        }
        let mut data = fs::read(bcd)?;

        // Thumbnail: same basename with .jpg; encrypt to .btl format.
        // from_switch_files with is_encrypted=true expects an already
        // encrypted thumbnail, so wrap the raw JPEG through Thumbnail2.
        let jpg = bcd.with_extension("jpg");
        let thumb = if jpg.is_file() {
            let raw = fs::read(&jpg)?;
            Some(Thumbnail2::from_decrypted(raw).take_encrypted())
        } else {
            None
        };

        let course = match Course2::from_switch_files(&mut data, thumb, true) {
            Ok(c) => c,
            Err(e) => {
                eprintln!("skip {} — unparseable course: {}", bcd.display(), e);
                continue;
            }
        };
        let title = course.get_course().get_header().get_title().to_string();
        save.add_course(slot, course)
            .with_context(|| format!("add_course slot {}", slot))?;
        println!("slot {:>2}: {} ({})", slot, title, bcd.file_name().unwrap().to_string_lossy());
        slot += 1;
        added += 1;
    }

    save.save().await.context("failed to write save")?;
    println!("done: {} courses registered in {}", added, save_dir.display());
    Ok(())
}
