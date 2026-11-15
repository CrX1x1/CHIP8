#terminal app to convert ch8 rom to packaged format
import sys
if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <rom_file> <output_file>")
    sys.exit(1)
with open(sys.argv[1], "rb") as file:
    rom = file.read()

bytes_list = ", ".join(f"0x{byte:02X}" for byte in rom)
template = f'''
try:
    from cpu import load_rom, run
except ImportError:
    try:
        from CPU import load_rom, run
    except ImportError:
        raise ImportError("import the damn module")
# autopackaged
ROM = bytes([{bytes_list}])
load_rom(ROM)
    run()
'''
with open(sys.argv[2], "w") as file:
        file.write(template)
print(f"Packaged ROM written to {sys.argv[2]}")
