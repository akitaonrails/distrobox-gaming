use std::error::Error;
use std::path::Path;

use gt4l_disc::{elf, iso::Iso, setup, Pins};

fn main() -> Result<(), Box<dyn Error>> {
    let mut args = std::env::args_os().skip(1);
    let disc = args.next().ok_or("usage: dg-gt4-recomp-prepare <disc.iso> <output-elf>")?;
    let output = args.next().ok_or("missing output ELF path")?;
    if args.next().is_some() {
        return Err("too many arguments".into());
    }
    let disc = Path::new(&disc);
    let output = Path::new(&output);
    let pins = Pins::embedded()?;
    let summary = setup::precheck(disc, &pins)?;
    let mut iso = Iso::open(disc)?;
    let core_entry = iso.find("CORE.GT4;1")?;
    let core = iso.read(&core_entry, 16 * 1024 * 1024)?;
    if core.len() as u64 != pins.core.size_bytes || elf::sha256_hex(&core) != pins.core.sha256 {
        return Err("disc CORE.GT4 differs from the pinned game code".into());
    }
    let image = elf::reconstruct(&core, &pins.policy)?;
    if image.len() as u64 != pins.elf.size_bytes || elf::sha256_hex(&image) != pins.elf.sha256 {
        return Err("reconstructed ELF differs from the pinned executable".into());
    }
    std::fs::write(output, image)?;
    println!("{} version {}: prepared {}", summary.serial, summary.version, output.display());
    Ok(())
}
