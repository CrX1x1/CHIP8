import ti_system
KEYMAP = {
    0x1: 72,
    0x2: 73,
    0x3: 74,
    0xC: 75,

    0x4: 82,
    0x5: 83,
    0x6: 84,
    0xD: 85,

    0x7: 92,
    0x8: 93,
    0x9: 94,
    0xE: 95,

    0xA: 102,
    0x0: 103,
    0xB: 104,
    0xF: 105,
}
def get_keymap(wait = False):
    k = ti_system.wait_key() if wait else ti_system.get_key(0)
    if k == 0:
        return None
    for chip_key, key in KEYMAP.items():
        if k == key:
            return chip_key
    return None
