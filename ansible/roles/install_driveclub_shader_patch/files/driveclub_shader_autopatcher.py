import glob
import os
import struct
import sys

MAGIC = 0x07230203

OP_ENTRY_POINT = 15
OP_EXECUTION_MODE = 16
OP_TYPE_INT = 21
OP_TYPE_VECTOR = 23
OP_TYPE_IMAGE = 25
OP_TYPE_POINTER = 32
OP_CONSTANT = 43
OP_VARIABLE = 59
OP_LOAD = 61
OP_COMPOSITE_EXTRACT = 81
OP_IMAGE_FETCH = 95
OP_IMAGE_WRITE = 99
OP_IMAGE_QUERY_SIZE = 104
OP_UGREATERTHAN = 172

EXEC_MODE_LOCAL_SIZE = 17
STORAGE_UNIFORM_CONSTANT = 0


def parse(words):
    if words[0] != MAGIC:
        raise ValueError("not a SPIR-V module")
    out = []
    i = 5
    while i < len(words):
        wc = words[i] >> 16
        if wc == 0:
            raise ValueError("zero-length instruction")
        out.append((i, wc, words[i] & 0xFFFF, list(words[i:i + wc])))
        i += wc
    return out


def load(path):
    raw = open(path, "rb").read()
    if len(raw) % 4:
        raise ValueError("size not a multiple of 4")
    return list(struct.unpack("<%dI" % (len(raw) // 4), raw))


def identify(words):
    """Return the analysis dict if this module is the de-interleave pass."""
    ins = parse(words)

    consts = {}
    for _, wc, op, w in ins:
        if op == OP_CONSTANT and wc >= 4:
            consts.setdefault(w[3], w[2])
    if 960 not in consts or 540 not in consts:
        return None

    has_fetch = any(op == OP_IMAGE_FETCH for _, _, op, _ in ins)
    has_write = any(op == OP_IMAGE_WRITE for _, _, op, _ in ins)
    if not (has_fetch and has_write):
        return None

    local = None
    for _, wc, op, w in ins:
        if op == OP_EXECUTION_MODE and wc >= 6 and w[2] == EXEC_MODE_LOCAL_SIZE:
            local = (w[3], w[4], w[5])
    if local != (8, 8, 1):
        return None

    if any(op == OP_IMAGE_QUERY_SIZE for _, _, op, _ in ins):
        return None

    u32 = None
    for _, wc, op, w in ins:
        if op == OP_TYPE_INT and wc >= 4 and w[2] == 32 and w[3] == 0:
            u32 = w[1]
    if u32 is None:
        return None
    v2u32 = None
    for _, wc, op, w in ins:
        if op == OP_TYPE_VECTOR and wc >= 4 and w[2] == u32 and w[3] == 2:
            v2u32 = w[1]
    if v2u32 is None:
        return None

    storage_types = set()
    for _, wc, op, w in ins:
        if op == OP_TYPE_IMAGE and wc >= 9 and w[7] == 2:
            storage_types.add(w[1])
    ptr_to_img = {}
    for _, wc, op, w in ins:
        if op == OP_TYPE_POINTER and wc >= 4 and w[2] == STORAGE_UNIFORM_CONSTANT:
            ptr_to_img[w[1]] = w[3]
    written = set()
    load_of = {}
    for _, wc, op, w in ins:
        if op == OP_LOAD and wc >= 4:
            load_of[w[2]] = (w[1], w[3])
        elif op == OP_IMAGE_WRITE and wc >= 4:
            written.add(w[1])
    dst_var = dst_img_type = None
    for res in written:
        if res in load_of:
            img_type, var = load_of[res]
            if img_type in storage_types:
                dst_var, dst_img_type = var, img_type
    if dst_var is None:
        return None
    for _, wc, op, w in ins:
        if op == OP_VARIABLE and wc >= 4 and w[2] == dst_var:
            if ptr_to_img.get(w[1]) != dst_img_type:
                return None

    cmps = {}
    for idx, (off, wc, op, w) in enumerate(ins):
        if op == OP_UGREATERTHAN and wc == 5:
            if w[3] == consts.get(960):
                cmps["w"] = idx
            elif w[3] == consts.get(540):
                cmps["h"] = idx
    if "w" not in cmps or "h" not in cmps:
        return None

    return {
        "ins": ins,
        "u32": u32,
        "v2u32": v2u32,
        "dst_var": dst_var,
        "dst_img_type": dst_img_type,
        "cmp_w": cmps["w"],
        "cmp_h": cmps["h"],
    }


def patch(words, a):
    bound = words[3]
    id_img, id_size, id_w, id_h = bound, bound + 1, bound + 2, bound + 3

    def enc(op, operands):
        return [((len(operands) + 1) << 16) | op] + operands

    inject = (
        enc(OP_LOAD, [a["dst_img_type"], id_img, a["dst_var"]])
        + enc(OP_IMAGE_QUERY_SIZE, [a["v2u32"], id_size, id_img])
        + enc(OP_COMPOSITE_EXTRACT, [a["u32"], id_w, id_size, 0])
        + enc(OP_COMPOSITE_EXTRACT, [a["u32"], id_h, id_size, 1])
    )

    first = min(a["cmp_w"], a["cmp_h"])
    out = list(words[:5])
    for idx, (off, wc, op, w) in enumerate(a["ins"]):
        if idx == first:
            out += inject
        if idx == a["cmp_w"]:
            w = list(w)
            w[3] = id_w
        elif idx == a["cmp_h"]:
            w = list(w)
            w[3] = id_h
        out += w
    out[3] = bound + 4
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]
        out_dir = os.path.join(src_dir, "patched")
    elif os.path.isdir(os.path.join(here, "dumps")):
        src_dir = os.path.join(here, "dumps")
        out_dir = os.path.join(here, "patch")
    else:
        src_dir = here
        out_dir = os.path.join(here, "patched")

    spvs = sorted(glob.glob(os.path.join(src_dir, "*.spv")))
    if not spvs:
        print("no .spv files in %s" % src_dir)
        print()
        print("put this tool in shadPS4's user\\shader folder (next to dumps),")
        print("or directly in the dump folder itself.")
        print("enable shader dumping and run the game first.")
        return 1

    found = []
    for path in spvs:
        try:
            words = load(path)
            a = identify(words)
        except Exception:
            continue
        if a:
            found.append((path, words, a))

    if not found:
        print("scanned %d modules in %s" % (len(spvs), src_dir))
        print("none matched the de-interleave pass.")
        print("either the game version differs, or the dump was taken before it ran.")
        return 1
    if len(found) > 1:
        print("more than one candidate, refusing to guess:")
        for p, _, _ in found:
            print("   %s" % os.path.basename(p))
        return 1

    path, words, a = found[0]
    out = patch(words, a)

    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, os.path.basename(path))
    with open(dst, "wb") as f:
        f.write(struct.pack("<%dI" % len(out), *out))

    print("scanned  %d modules in %s" % (len(spvs), src_dir))
    print("matched  %s" % os.path.basename(path))
    print("written  %s" % dst)
    print("         id bound %d -> %d, %d words -> %d"
          % (words[3], out[3], len(words), len(out)))
    print()
    if os.path.basename(out_dir) == "patch":
        print("SUCCESS")
    else:
        print("SUCCESS - copy the shader from the patched folder "
              "into the *\\ShadPS4\\user\\shader folder")
    return 0


if __name__ == "__main__":
    sys.exit(main())
