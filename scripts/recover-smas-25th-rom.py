#!/usr/bin/env python3
# Manual one-off: recover the exact Super Mario All-Stars 25th-Anniversary USA
# SNES ROM (sha256 411c7036…) that install_smas_recomp requires, from the user's
# own "Super Mario All-Stars: Limited Edition" Wii disc. NOT invoked by any role
# (the role only verifies the staged ROM's sha256); run it by hand to re-stage
# the ROM on the NAS if it is ever lost. See docs/smas-recomp.md.
#
# Self-contained Python 3 port of vcromclaim (github.com/Plombo/vcromclaim):
#   - lzh8.py  (hcs's LZH8 / LZ77+Huffman decompressor, ported by Bryan Cain)
#   - snesrestore.py + brrencode3.py (re-inject BRR audio from the PCM pack)
# Inputs: files/content5/LZH8SVME.rom + LZH8SVME.pcm from the disc (extract the
# disc filesystem with `nodtool extract <disc> out/`). Usage:
#   recover-smas-25th-rom.py LZH8SVME.rom LZH8SVME.pcm out.sfc
import sys, struct, io, hashlib
from array import array

TARGET = "411c7036750fbc79d60b84602414dbe713074de8204d3c4a5ad762679c103c61"

# ---------------- LZH8 decompressor (hcs) ----------------
LENBITS, DISPBITS = 9, 5
LENCNT, DISPCNT = (1 << LENBITS), (1 << DISPBITS)

class Bits:
    def __init__(self, data):
        self.data = data; self.off = 0; self.pool = 0; self.left = 0
    def seek(self, o): self.off = o
    def tell(self): return self.off
    def get(self, bit_count):
        out = 0; produced = 0
        while produced < bit_count:
            if self.left == 0:
                self.pool = self.data[self.off]; self.off += 1; self.left = 8
            n = bit_count - produced
            this_round = n if self.left > n else self.left
            out = (out << this_round) | ((self.pool >> (self.left - this_round)) & ((1 << this_round) - 1))
            self.left -= this_round; produced += this_round
        return out

def lzh8_decompress(data):
    b = Bits(data)
    header = struct.unpack_from("<I", data, 0)[0]
    if (header & 0xFF) != 0x40: raise ValueError("not LZH8")
    uncompressed_length = header >> 8
    pos = 4
    if uncompressed_length == 0:
        uncompressed_length = struct.unpack_from("<I", data, 4)[0]; pos = 8
    outbuf = array('B', bytes(uncompressed_length))

    length_decode_table_size = LENCNT * 2
    size_pos = pos  # start of accounting includes the 2-byte size field
    length_table_bytes = (struct.unpack_from("<H", data, pos)[0] + 1) * 4
    pos += 2
    length_decode_table = array('H', bytes(length_decode_table_size * 2))  # 1024 shorts

    b.seek(pos); b.left = 0
    start = size_pos; i = 1
    while (b.tell() - start) < length_table_bytes:
        if i >= length_decode_table_size: break
        length_decode_table[i] = b.get(LENBITS); i += 1
    pos = start + length_table_bytes
    b.seek(pos); b.left = 0

    size_pos = pos  # start of accounting includes the 1-byte size field
    displen_table_bytes = (data[pos] + 1) * 4
    pos += 1
    displen_decode_table = array('B', bytes(DISPCNT * 2))
    b.seek(pos); b.left = 0
    start = size_pos; i = 1
    while (b.tell() - start) < displen_table_bytes:
        if i >= DISPCNT * 2: break
        displen_decode_table[i] = b.get(DISPBITS); i += 1
    pos = start + displen_table_bytes
    b.seek(pos); b.left = 0

    bytes_decoded = 0
    while bytes_decoded < uncompressed_length:
        length_table_offset = 1
        while True:
            next_child = b.get(1)
            payload = length_decode_table[length_table_offset] & 0x7F
            next_off = (length_table_offset // 2 * 2) + (payload + 1) * 2 + bool(next_child)
            isleaf = length_decode_table[length_table_offset] & (0x100 >> next_child)
            if isleaf:
                length = length_decode_table[next_off]
                if 0x100 > length:
                    outbuf[bytes_decoded] = length; bytes_decoded += 1
                else:
                    length = (length & 0xFF) + 3
                    d_off = 1
                    while True:
                        nd_child = b.get(1)
                        d_payload = displen_decode_table[d_off] & 0x7
                        nd_off = (d_off // 2 * 2) + (d_payload + 1) * 2 + bool(nd_child)
                        nd_isleaf = displen_decode_table[d_off] & (0x10 >> nd_child)
                        if nd_isleaf:
                            displen = displen_decode_table[nd_off]
                            displacement = 0
                            if displen != 0:
                                displacement = 1
                                for _ in range(displen - 1, 0, -1):
                                    displacement = (displacement << 1) | b.get(1)
                            for _ in range(length):
                                outbuf[bytes_decoded] = outbuf[bytes_decoded - displacement - 1]
                                bytes_decoded += 1
                                if bytes_decoded >= uncompressed_length: break
                            break
                        else:
                            assert nd_off != d_off; d_off = nd_off
                break
            else:
                assert next_off != length_table_offset; length_table_offset = next_off
    return bytes(outbuf)

# ---------------- BRR encoder (Bregalad/Cain) ----------------
class BRREncoder:
    def __init__(self, pcm): self.pcm = pcm; self.p1 = 0; self.p2 = 0
    def sshort(self, n):
        if n > 0x7FFF: return n - 0x10000
        elif n < -0x8000: return n & 0x7FFF
        else: return n
    def clamp_16(self, n):
        if n > 0x7FFF: return 0x7FFF - (n >> 24)
        else: return n
    def ADPCMBlockMash(self, PCMData):
        smin = kmin = 0; dmin = 2**31
        for s in range(13, 0, -1):
            for k in range(4):
                d = self.ADPCMMash(s, k, PCMData, False)
                if d < dmin: kmin = k; dmin = d; smin = s
                if dmin == 0.0: break
            if dmin == 0.0: break
        self.BRRBuffer[0] = (smin << 4) | (kmin << 2)
        self.ADPCMMash(smin, kmin, PCMData, True)
    def ADPCMMash(self, shiftamount, filter, PCMData, write):
        d2 = 0.0; vlin = 0; l1 = self.p1; l2 = self.p2; step = 1 << shiftamount
        for i in range(16):
            if filter == 0: vlin = 0
            elif filter == 1:
                vlin = l1 >> 1; vlin += (-l1) >> 5
            elif filter == 2:
                vlin = l1; vlin += (-(l1 + (l1 >> 1))) >> 5; vlin -= l2 >> 1; vlin += l2 >> 5
            else:
                vlin = l1; vlin += (-(l1 + (l1 << 2) + (l1 << 3))) >> 7; vlin -= l2 >> 1; vlin += (l2 + (l2 >> 1)) >> 4
            d = (PCMData[i] >> 1) - vlin; da = abs(d)
            if da > 16384 and da < 32768: d = d - 32768 * (d >> 24)
            dp = d + (step << 2) + (step >> 2); c = 0
            if dp > 0:
                if step > 1: c = dp // (step >> 1)
                else: c = dp << 1
                if c > 15: c = 15
            c -= 8
            dp = (c << (shiftamount - 1))
            if shiftamount > 12: dp = (dp >> 14) & ~0x7FF
            c &= 0x0f; l2 = l1; l1 = self.sshort(self.clamp_16(vlin + dp) * 2)
            d = PCMData[i] - l1; d2 += float(d) * d
            if write: self.BRRBuffer[(i >> 1) + 1] |= c << (4 - ((i & 0x01) << 2))
        if write: self.p2 = l2; self.p1 = l1
        return d2
    def encode_block(self, offset):
        self.pcm.seek(offset * 2); samples2 = self.pcm.read(32)
        if len(samples2) != 32: raise ValueError('invalid PCM offset %d' % offset)
        samples2 = struct.unpack('>16h', samples2)
        self.BRRBuffer = [0]*9
        self.ADPCMBlockMash(samples2)
        return bytes(self.BRRBuffer)

# ---------------- SNES restore (Cain) ----------------
def restore_brr_samples(vcrom_bytes, pcm_bytes):
    full = vcrom_bytes
    samplestart = full.find(b'PCMF')
    if samplestart < 0: raise ValueError("no PCMF markers in ROM")
    buf = bytearray(full[samplestart:])
    enc = BRREncoder(io.BytesIO(pcm_bytes))
    lastpcmoffset = None
    while True:
        index = buf.find(b'PCMF')
        if index < 0: break
        _pcmf, pcmoffset = struct.unpack('<4sI', bytes(buf[index:index+8]))
        pcmoffset &= 0xffffff
        if pcmoffset % 16 or (lastpcmoffset is not None and pcmoffset < lastpcmoffset):
            pcmoffset = (lastpcmoffset or 0) + 16
        brrsample = enc.encode_block(pcmoffset)
        if len(brrsample) != 9: raise ValueError("bad BRR len")
        flags = buf[index + 7]
        b0 = brrsample[0]
        if flags & 1: b0 |= 1
        if flags & 2: b0 |= 2
        brrsample = bytes([b0]) + brrsample[1:]
        buf[index:index+9] = brrsample
        lastpcmoffset = pcmoffset
    return full[:samplestart] + bytes(buf)

def snes_checksum(d):
    stored_s = d[0x7FDE] | (d[0x7FDF] << 8)
    s = sum(d) & 0xFFFF
    return stored_s, s, (stored_s == s)

if __name__ == '__main__':
    rom_c, pcm_c, out = sys.argv[1], sys.argv[2], sys.argv[3]
    print("decompressing ROM..."); vcrom = lzh8_decompress(open(rom_c, 'rb').read())
    print(f"  rom decompressed: {len(vcrom)} bytes (0x{len(vcrom):X})")
    print("decompressing PCM..."); pcm = lzh8_decompress(open(pcm_c, 'rb').read())
    print(f"  pcm decompressed: {len(pcm)} bytes (0x{len(pcm):X})")
    print(f"  PCMF markers in rom: {vcrom.count(b'PCMF')}")
    print("restoring BRR samples..."); rom = restore_brr_samples(vcrom, pcm)
    open(out, 'wb').write(rom)
    h = hashlib.sha256(rom).hexdigest()
    stored, calc, ok = snes_checksum(rom)
    print(f"\noutput: {out}")
    print(f"  size   = {len(rom)} (0x{len(rom):X})")
    print(f"  sha256 = {h}")
    print(f"  TARGET = {TARGET}")
    print(f"  MATCH  = {'*** YES ***' if h == TARGET else 'no'}")
    print(f"  internal checksum stored={stored:04X} calc={calc:04X} valid={ok}")
