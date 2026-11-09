//! Headless driver for the patcher's modules: builds the Daytona USA Ultimate
//! disc from two cue sheets without the Tauri GUI (upstream's is Windows-only).
//! The modules are upstream's, compiled unchanged from the staged source tree.
#[path = "../../src-tauri/src/builder.rs"]
mod builder;
#[path = "../../src-tauri/src/cdrom.rs"]
mod cdrom;
#[path = "../../src-tauri/src/disc.rs"]
mod disc;
#[path = "../../src-tauri/src/patch.rs"]
mod patch;

use std::path::Path;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 4 {
        eprintln!("usage: daytona-headless CCE.cue DUSA.cue OUTDIR");
        std::process::exit(2);
    }
    let mut last = -1.0;
    let result = builder::build(
        Path::new(&args[1]),
        Path::new(&args[2]),
        Path::new(&args[3]),
        |p| {
            if let Some(line) = p.log {
                println!("{line}");
            } else if p.fraction - last >= 0.1 {
                last = p.fraction;
                println!("{}: {} - {:.0}%", p.stage, p.detail, p.fraction * 100.0);
            }
        },
    );
    match result {
        Ok(done) => println!("done: {} ({})", done.cue, done.dir),
        Err(e) => {
            eprintln!("error: {e}");
            std::process::exit(1);
        }
    }
}
