#!/usr/bin/env node
// smm1 course injector — adds extracted course folders to a Cemu SMM1 save.
//
// Each course folder must contain course_data.cdt, course_data_sub.cdt,
// thumbnail0.tnl, thumbnail1.tnl (the layout cemu-smm's loadCourse and
// SMM1 itself expect). addCourseFromFs assigns the next free slot,
// updates the slot order table, and rewrites the save.dat CRC.
//
// Usage: node inject.js <smm1_save_dir> <courses_parent_dir>
//   save dir = .../mlc01/usr/save/00050000/1018dd00/user/80000001

const smm = require('cemu-smm');
const fs = require('fs');
const path = require('path');

(async () => {
  const [saveDir, coursesDir] = process.argv.slice(2);
  if (!saveDir || !coursesDir) {
    console.error('usage: node inject.js <save_dir> <courses_parent_dir>');
    process.exit(2);
  }
  if (!fs.existsSync(path.join(saveDir, 'save.dat'))) {
    console.error(`no save.dat in ${saveDir} — launch SMM1 once in Cemu first`);
    process.exit(3);
  }

  const save = await smm.loadSave(saveDir);
  await save.loadCourses();

  const dirs = fs.readdirSync(coursesDir)
    .map(d => path.join(coursesDir, d))
    .filter(d => fs.statSync(d).isDirectory()
      && fs.existsSync(path.join(d, 'course_data.cdt')))
    .sort();

  if (dirs.length === 0) {
    console.error(`no course folders (with course_data.cdt) in ${coursesDir}`);
    process.exit(4);
  }

  let added = 0;
  for (const dir of dirs) {
    try {
      const slot = await save.addCourseFromFs(dir);
      console.log(`slot ${String(slot).padStart(3, ' ')}: ${path.basename(dir)}`);
      added++;
    } catch (err) {
      if (/No empty slot/.test(String(err))) {
        console.error('save full (120 slots) — stopping');
        break;
      }
      console.error(`skip ${path.basename(dir)}: ${err.message || err}`);
    }
  }
  console.log(`done: ${added} courses added`);
})().catch(err => { console.error(err); process.exit(1); });
