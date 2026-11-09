#!/usr/bin/env python3
# PG32UCDM MCM311: make "Auto KVM Detection" follow the per-input USB port assignment
# (OSD: USB Setup > KVM > Auto KVM Detection > USB-C / DisplayPort / HDMI-1 / HDMI-2).
#
# KVM_AutoPoll (0x8610bfa0) only applies that assignment when two status flags
# (0xa00088f0 == 1, 0xa003f83c == 0) are set. This removes that condition, and the
# edge rules after it, so the KVM port always follows the input on screen while
# Auto is on and a stable signal is present.
#
# usage: make_autokvm.py <ASUS_PG32UCDM_Project.bin (MCM311 ISP image)> <output.bin>
import hashlib
import sys

BASE = 0x86000000
PATCHES = [
    # 0x8610bfe2: btnez 0x8610c012  ->  b 0x8610bff0 (skip flag check, go to per-input lookup)
    (0x8610bfe2, bytes.fromhex('1761'), bytes.fromhex('0610')),
    # 0x8610c0ce: b 0x8610c012      ->  b 0x8610c078 (skip edge rules, apply looked-up port)
    (0x8610c0ce, bytes.fromhex('a117'), bytes.fromhex('d417')),
]


def main():
    src, dst = sys.argv[1], sys.argv[2]
    img = bytearray(open(src, 'rb').read())

    if len(img) != 0x1F0000 or img[0xF800:0xF806] != b'MCM311':
        sys.exit('not the MCM311 PG32UCDM image')

    if img[-1] != 0xFF:
        sys.exit('expected the OneKeyUpdate ISP image (last byte 0xFF), not the USB-stick image')

    for addr, old, new in PATCHES:
        off = addr - BASE
        if img[off:off + len(old)] != old:
            sys.exit(f'unexpected bytes at 0x{addr:08x}: {img[off:off + len(old)].hex()}')
        img[off:off + len(new)] = new

    open(dst, 'wb').write(img)
    print('patched ->', dst)
    print('sha256  ', hashlib.sha256(img).hexdigest())


if __name__ == '__main__':
    main()
