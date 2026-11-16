import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <rom_file>")
    sys.exit(1)

rom_file = sys.argv[1]
try:
    with open(rom_file, "rb") as file:
        rom = file.read()
except FileNotFoundError:
    print(f"ROM file not found: {rom_file}")
    sys.exit(1)
pc = 0x200
i = 0
print(f"{'ADDR':<6} {'HEX':<6} {'MNEMONIC':<10}")
print("\n")

while i < len(rom):
    if i+1 >= len(rom):
        print(f"ROM ends with an incomplete instruction at {pc:04X}")
        break
    opcode = (rom[i] << 8) | rom[i + 1]

    op = (opcode & 0xF000) >> 12
    x = (opcode & 0x0F00) >> 8
    y = (opcode & 0x00F0) >> 4
    n = opcode & 0x000F
    kk = opcode & 0x00FF
    nnn = opcode & 0x0FFF

    mnemonic = "UNKNOWN"
    if opcode == 0x00E0:
        mnemonic = "CLS"
    elif opcode == 0x00EE:
        mnemonic = "RET"
    elif op == 0x1:
        mnemonic = f"JP {nnn:03X}"
    elif op == 0x2:
        mnemonic = f"CALL {nnn:03X}"
    elif op == 0x3:
        mnemonic = f"SE V{x:X}, {kk:02X}"
    elif op == 0x4:
        mnemonic = f"SNE V{x:X}, {kk:02X}"
    elif op == 0x5 and n == 0x0:
        mnemonic = f"SE V{x:X}, V{y:X}"
    elif op == 0x6:
        mnemonic = f"LD V{x:X}, {kk:02X}"
    elif op == 0x7:
        mnemonic = f"ADD V{x:X}, {kk:02X}"
    elif op == 0x8:
        sec_ops = {
            0x0: f"LD V{x:X}, V{y:X}",
            0x1: f"OR V{x:X}, V{y:X}",
            0x2: f"AND V{x:X}, V{y:X}",
            0x3: f"XOR V{x:X}, V{y:X}",
            0x4: f"ADD V{x:X}, V{y:X}",
            0x5: f"SUB V{x:X}, V{y:X}",
            0x6: f"SHR V{x:X}, V{y:X}",
            0x7: f"SUBN V{x:X}, V{y:X}",
            0xE: f"SHL V{x:X}, V{y:X}",
        }
        mnemonic = sec_ops.get(n, f"UNKNOWN 0x{opcode:04X}")
    elif op == 0x9 and n == 0x0:
        mnemonic = f"SNE V{x:X}, V{y:X}"
    elif op == 0xA:
        mnemonic = f"LD I, {nnn:03X}"
    elif op == 0xB:
        mnemonic = f"JP V0, {nnn:03X}"
    elif op == 0xC:
        mnemonic = f"RND V{x:X}, {kk:02X}"
    elif op == 0xD:
        mnemonic = f"DRW V{x:X}, V{y:X}, {n}"
    elif op == 0xE:
        if kk == 0x9E:
            mnemonic = f"SKP V{x:X}"
        elif kk == 0xA1:
            mnemonic = f"SKNP V{x:X}"
    elif op == 0xF:
        if n == 0x07:
            mnemonic = f"LD V{x:X}, DT"
        elif n == 0x0A:
            mnemonic = f"LD V{x:X}, K"
        elif n == 0x15:
            mnemonic = f"LD DT, V{x:X}"
        elif n == 0x18:
            mnemonic = f"LD ST, V{x:X}"
        elif n == 0x1E:
            mnemonic = f"ADD I, V{x:X}"
        elif n == 0x29:
            mnemonic = f"LD F, V{x:X}"
        elif n == 0x33:
            mnemonic = f"LD BCD, V{x:X}"
        elif n == 0x55:
            mnemonic = f"LD [I], V0, V1, V2, V3, V4, V5, V6, V7"
        elif n == 0x65:
            mnemonic = f"LD V0, V1, V2, V3, V4, V5, V6, V7, [I]"
    else:
        mnemonic = f"DATA 0x{opcode:04X}"
    print(f"0x{pc:04X}: 0x{opcode:04X} {mnemonic}")
    pc += 2
    i += 1
