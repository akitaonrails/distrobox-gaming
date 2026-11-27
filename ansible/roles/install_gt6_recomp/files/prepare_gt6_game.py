#!/usr/bin/env python3
"""Prepare Gran Turismo 6 (BCES01893 1.22) game data for Project Grand Tourer Advanced."""

import hashlib
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time

PS3_PKG_AES_KEY = bytes.fromhex("2E7B71D7C9C9A14EA3221F188828B8F8")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sfo_app_ver(sfo_path: str) -> str:
    try:
        data = open(sfo_path, "rb").read()
    except OSError:
        return ""
    if len(data) < 20 or data[:4] != b"\x00PSF":
        return ""
    key_off, data_off, count = struct.unpack("<III", data[8:20])
    for i in range(count):
        base = 20 + i * 16
        if base + 16 > len(data):
            break
        ko, _, dl, _, do = struct.unpack("<HHIII", data[base : base + 16])
        kp = key_off + ko
        ke = data.index(b"\x00", kp)
        key = data[kp:ke].decode("utf-8", errors="replace")
        if key in ("APP_VER", "VERSION"):
            val = data[data_off + do : data_off + do + dl].split(b"\x00", 1)[0].decode("utf-8", errors="replace")
            if key == "APP_VER":
                return val
    return ""


def _decrypt_ctr(fh, data_offset: int, base_iv: bytes, rel_offset: int, length: int) -> bytes:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    block_index = rel_offset // 16
    block_offset = rel_offset % 16
    iv_int = int.from_bytes(base_iv, "big") + block_index
    iv = (iv_int & ((1 << 128) - 1)).to_bytes(16, "big")
    read_len = length + block_offset
    padded = ((read_len + 15) // 16) * 16
    fh.seek(data_offset + block_index * 16)
    enc = fh.read(padded)
    dec = Cipher(algorithms.AES(PS3_PKG_AES_KEY), modes.CTR(iv)).decryptor()
    out = dec.update(enc) + dec.finalize()
    return out[block_offset : block_offset + length]


def extract_pkg(pkg_path: str, dest_dir: str) -> None:
    with open(pkg_path, "rb") as fh:
        hdr = fh.read(0xC0)
        if hdr[:4] != b"\x7fPKG":
            raise RuntimeError(f"Not a PS3 PKG: {pkg_path}")
        item_count = struct.unpack(">I", hdr[0x14:0x18])[0]
        data_offset = struct.unpack(">Q", hdr[0x20:0x28])[0]
        data_size = struct.unpack(">Q", hdr[0x28:0x30])[0]
        base_iv = hdr[0x70:0x80]

        meta_sz = min(item_count * 96, data_size)
        meta = _decrypt_ctr(fh, data_offset, base_iv, 0, meta_sz)
        entries = []
        for i in range(item_count):
            o = i * 32
            name_off, name_sz = struct.unpack(">II", meta[o : o + 8])
            file_off, file_sz = struct.unpack(">QQ", meta[o + 8 : o + 24])
            ctype = struct.unpack(">I", meta[o + 24 : o + 28])[0]
            if name_off + name_sz <= len(meta):
                name = meta[name_off : name_off + name_sz].decode("utf-8", errors="replace").rstrip("\x00")
            else:
                name = _decrypt_ctr(fh, data_offset, base_iv, name_off, name_sz).decode("utf-8", errors="replace").rstrip("\x00")
            is_dir = file_sz == 0 and (ctype & 0xFF) in (0x04, 0x12)
            entries.append((name, file_off, file_sz, is_dir))

        os.makedirs(dest_dir, exist_ok=True)
        for name, _, _, is_dir in entries:
            if is_dir or name.endswith("/"):
                os.makedirs(os.path.join(dest_dir, name), exist_ok=True)

        for name, file_off, file_sz, is_dir in entries:
            if is_dir or file_sz == 0:
                continue
            target = os.path.join(dest_dir, name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            remaining = file_sz
            offset = file_off
            with open(target, "wb") as out:
                while remaining > 0:
                    chunk = min(1 << 20, remaining)
                    out.write(_decrypt_ctr(fh, data_offset, base_iv, offset, chunk))
                    offset += chunk
                    remaining -= chunk


def cmd_extract_updates(args: list[str]) -> int:
    title_dir = args[0]
    pkgs = sorted(args[1:], key=lambda p: os.path.basename(p))
    if sfo_app_ver(os.path.join(title_dir, "PARAM.SFO")) == "01.22":
        usrdir = os.path.join(title_dir, "USRDIR")
        if os.path.exists(os.path.join(usrdir, "TPPS-01.22", "EMAIN.SELF")) or (
            os.path.exists(os.path.join(usrdir, "EMAIN.SELF"))
            and os.path.getsize(os.path.join(usrdir, "EMAIN.SELF")) == 9209104
        ):
            print("SKIP: BCES01893 already at 01.22")
            return 0
    for idx, pkg in enumerate(pkgs, 1):
        print(f"[{idx}/{len(pkgs)}] Extracting {os.path.basename(pkg)}", flush=True)
        extract_pkg(pkg, title_dir)
    ver = sfo_app_ver(os.path.join(title_dir, "PARAM.SFO"))
    if ver != "01.22":
        raise RuntimeError(f"Expected APP_VER 01.22 after update extraction, got {ver!r}")
    print("EXTRACTED: BCES01893 updated to 01.22")
    return 0


def cmd_relocate_prx(args: list[str]) -> int:
    prx_path, out_img, expected_prx_sha, expected_img_sha = args
    d = open(prx_path, "rb").read()
    got_prx = hashlib.sha256(d).hexdigest()
    if got_prx != expected_prx_sha.lower():
        raise RuntimeError(f"libsre.prx sha256 mismatch: {got_prx} != {expected_prx_sha}")
    if len(d) < 0x40 or d[:2] != b"\x7fE" or d[4] != 2 or d[5] != 2:
        raise RuntimeError("not a decrypted 64-bit big-endian PRX")

    base_addr = 0x30000000
    phoff = struct.unpack(">Q", d[0x20:0x28])[0]
    phnum = struct.unpack(">H", d[0x38:0x3A])[0]
    loads = []
    rela_off = rela_sz = 0
    for i in range(phnum):
        o = phoff + i * 0x38
        ptype = struct.unpack(">I", d[o : o + 4])[0]
        if ptype == 1:
            loads.append(struct.unpack(">QQQQ", d[o + 8 : o + 24] + d[o + 32 : o + 48]))
        elif ptype == 0x700000A4:
            rela_off = struct.unpack(">Q", d[o + 8 : o + 16])[0]
            rela_sz = struct.unpack(">Q", d[o + 32 : o + 40])[0]

    top = max(vaddr + memsz for _, vaddr, _, memsz in loads)
    img = bytearray(top)
    seg_base = []
    for off, vaddr, filesz, _ in loads:
        img[vaddr : vaddr + filesz] = d[off : off + filesz]
        seg_base.append(base_addr + vaddr)

    for i in range(rela_sz // 24):
        o = rela_off + i * 24
        offset = struct.unpack(">Q", d[o : o + 8])[0]
        idx_val = d[o + 10]
        idx_addr = d[o + 11]
        rtype = struct.unpack(">I", d[o + 12 : o + 16])[0]
        ptr = struct.unpack(">Q", d[o + 16 : o + 24])[0]
        target = seg_base[idx_addr] - base_addr + offset
        value = (0 if idx_val == 0xFF else seg_base[idx_val]) + ptr
        if rtype == 1:
            img[target : target + 4] = struct.pack(">I", value & 0xFFFFFFFF)
        elif rtype == 4:
            img[target : target + 2] = struct.pack(">H", value & 0xFFFF)
        elif rtype == 5:
            img[target : target + 2] = struct.pack(">H", (value >> 16) & 0xFFFF)
        elif rtype == 6:
            img[target : target + 2] = struct.pack(">H", ((value + 0x8000) >> 16) & 0xFFFF)
        elif rtype == 44:
            img[target : target + 8] = struct.pack(">Q", value & 0xFFFFFFFFFFFFFFFF)
        else:
            raise RuntimeError(f"Unsupported PRX relocation type {rtype}")

    got_img = hashlib.sha256(img).hexdigest()
    if got_img != expected_img_sha.lower():
        raise RuntimeError(f"libsre_image.bin sha256 mismatch: {got_img} != {expected_img_sha}")
    os.makedirs(os.path.dirname(out_img), exist_ok=True)
    with open(out_img, "wb") as fh:
        fh.write(img)
    print(f"RELOCATED: {out_img} ({len(img)} bytes, sha256 verified)")
    return 0


def cmd_decrypt_emain(args: list[str]) -> int:
    rpcs3_bin, disc_dir, dev_flash_dir, title_dir, out_elf, expected_sha = args
    if os.path.exists(out_elf) and sha256_file(out_elf) == expected_sha.lower():
        print("SKIP: EMAIN.ELF already decrypted and verified")
        return 0

    usrdir = os.path.join(title_dir, "USRDIR")
    self_src = os.path.join(usrdir, "TPPS-01.22", "EMAIN.SELF")
    if not os.path.exists(self_src):
        self_src = os.path.join(usrdir, "EMAIN.SELF")
    loader_src = os.path.join(usrdir, "EBOOT.BIN")
    if not os.path.exists(self_src) or not os.path.exists(loader_src):
        raise RuntimeError(f"Missing 1.22 EBOOT.BIN or EMAIN.SELF under {usrdir}")

    tmp = tempfile.mkdtemp(prefix="gt6-klic-", dir=os.path.dirname(out_elf))
    try:
        cfg_root = os.path.join(tmp, "cfg")
        cfg_dir = os.path.join(cfg_root, "rpcs3")
        small_hdd0 = os.path.join(tmp, "hdd0")
        small_title = os.path.join(small_hdd0, "game", "BCES01893")
        work_dir = os.path.join(tmp, "work")
        os.makedirs(os.path.join(small_title, "USRDIR"), exist_ok=True)
        os.makedirs(cfg_dir, exist_ok=True)
        os.makedirs(work_dir, exist_ok=True)

        shutil.copy2(os.path.join(title_dir, "PARAM.SFO"), os.path.join(small_title, "PARAM.SFO"))
        shutil.copy2(loader_src, os.path.join(small_title, "USRDIR", "EBOOT.BIN"))
        shutil.copy2(self_src, os.path.join(small_title, "USRDIR", "EMAIN.SELF"))
        shutil.copy2(self_src, os.path.join(work_dir, "EMAIN.SELF"))
        os.symlink(dev_flash_dir, os.path.join(cfg_dir, "dev_flash"))

        with open(os.path.join(cfg_dir, "vfs.yml"), "w") as fh:
            fh.write(f'/dev_hdd0/: "{small_hdd0}/"\n')
            fh.write(f'/dev_flash/: "{dev_flash_dir}/"\n')
        with open(os.path.join(cfg_dir, "games.yml"), "w") as fh:
            fh.write(f'BCES01893: "{disc_dir}/"\n')
        with open(os.path.join(cfg_dir, "config.yml"), "w") as fh:
            fh.write(
                "Core:\n"
                "  PPU Decoder: Interpreter (static)\n"
                "  SPU Decoder: Interpreter (static)\n"
                "Video:\n"
                '  Renderer: "Null"\n'
                "Audio:\n"
                '  Renderer: "Null"\n'
            )

        env = os.environ.copy()
        env["APPIMAGE_EXTRACT_AND_RUN"] = "1"
        env["XDG_CONFIG_HOME"] = cfg_root
        env["XDG_CACHE_HOME"] = os.path.join(tmp, "cache")
        os.makedirs(env["XDG_CACHE_HOME"], exist_ok=True)

        cmd = [rpcs3_bin, "--no-gui", os.path.join(small_title, "USRDIR", "EBOOT.BIN")]
        if shutil.which("xvfb-run"):
            cmd = ["xvfb-run", "-a"] + cmd
        proc = subprocess.Popen(cmd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        klic = None
        log_candidates = [
            os.path.join(env["XDG_CACHE_HOME"], "rpcs3", "RPCS3.log"),
            os.path.join(cfg_dir, "RPCS3.log"),
        ]
        deadline = time.monotonic() + 180.0
        try:
            while time.monotonic() < deadline:
                for lp in log_candidates:
                    if os.path.exists(lp):
                        text = open(lp, "r", errors="replace").read()
                        m = re.search(r"KLIC=0x([0-9A-Fa-f]{32})", text)
                        if m:
                            klic = m.group(1)
                            break
                if klic:
                    break
                if proc.poll() is not None:
                    break
                time.sleep(0.25)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

        if not klic:
            raise RuntimeError("Could not obtain EMAIN.SELF licence key from RPCS3 loader boot")

        dec_cmd = [rpcs3_bin, "--decrypt", os.path.join(work_dir, "EMAIN.SELF")]
        dec = subprocess.run(dec_cmd, env=env, input=f"{klic}\n", text=True, capture_output=True, timeout=120)
        klic = None
        elf_tmp = os.path.join(work_dir, "EMAIN.elf")
        if dec.returncode != 0 or not os.path.exists(elf_tmp):
            raise RuntimeError(f"rpcs3 --decrypt failed (rc={dec.returncode}): {dec.stderr}")
        got = sha256_file(elf_tmp)
        if got != expected_sha.lower():
            raise RuntimeError(f"Decrypted EMAIN.ELF sha256 mismatch: {got} != {expected_sha}")
        os.makedirs(os.path.dirname(out_elf), exist_ok=True)
        shutil.copy2(elf_tmp, out_elf)
        print(f"DECRYPTED: {out_elf} (sha256 verified)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: prepare_gt6_game.py <extract-updates|relocate-prx|decrypt-emain> ...", file=sys.stderr)
        return 2
    sub = sys.argv[1]
    if sub == "extract-updates":
        return cmd_extract_updates(sys.argv[2:])
    if sub == "relocate-prx":
        return cmd_relocate_prx(sys.argv[2:])
    if sub == "decrypt-emain":
        return cmd_decrypt_emain(sys.argv[2:])
    print(f"unknown subcommand: {sub}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
