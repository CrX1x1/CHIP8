import time
import ti_graphics
import ti_system
import random
from CORE import * #intentional

#test program
ROM = bytes([
    # Wait for a key → store in V0
    0xF0, 0x0A,          # Fx0A  LD V0, K

    # Clear screen
    0x00, 0xE0,          # CLS

    # Point I at the font for the key that was pressed
    0xF0, 0x29,          # Fx29  LD F, V0

    # Draw it at (10, 10)
    0x60, 0x0A,          # LD V0, 10
    0x61, 0x0A,          # LD V1, 10
    0xD0, 0x15,          # DRW V0, V1, 5

    # Loop forever
    0x12, 0x00           # JP 0x200  (jump back to the wait)
])# AI made this, probably common info though

#configs
SCALE = 4 #4x4 per pixel, calculator is 320x240
FPS = 60
INSTRS_PER_FRAME = 12
STICKY_KEY = 1 #in instruction cycles

#states and registers
memory = bytearray(4096)
V = bytearray(16)
I = 0
PC = 0x200
stack = []
delay_timer = 0
sound_timer = 0 #heh, the calculator deosn't even have sounds, maybe with ti-innovator
timer = 0 # for keys
prev_key = None

display = bytearray(64 * 32) #binary
draw_flag = False

FONT = [ #err, autocomplete finished this, i dunno if it's right, maybe later
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80, # F
]

#helpers
def load_font():
    for i, char in enumerate(FONT):
        memory[i] = char
def load_rom(rom):
    for i, byte in enumerate(rom):
        memory[0x200 + i] = byte
def clear_display():
    global draw_flag
    for i in range(len(display)):
        display[i] = 0
    draw_flag = True
def draw_sprite(x, y, sprite):
    global draw_flag, I
    V[0xF] = 0
    for row in range(sprite):
        byte = memory[I + row]
        for col in range(8):
            if byte & (0x80 >> col):
                px = (x+col) % 64
                py = (y+row) % 32
                idx = py * 64 + px
                if display[idx]:
                    V[0xF] = 1#collision
                display[idx] ^= 1
    draw_flag = True
    #print("Sprite drawn at", x, y)
    # done by autocomplete, verify later
def render():
    ti_graphics.cls()
    for y in range(32):
        for x in range(64):
            if display[y * 64 + x]:
                ti_graphics.fillRect(x * SCALE, y * SCALE, SCALE, SCALE)
    # no need for pause lol, maybe for debugging
def get_sticky_key():
    global STICKY_KEY, timer, prev_key
    key = get_keymap()
    if key is not None:
        prev_key = key
        timer = STICKY_KEY
    if timer > 0:
        timer -= 1
        key = prev_key
    else:
        key = None
    return key
# interpreter
def execute(opcode):
    global PC, I, STICKY_KEY, delay_timer, sound_timer, timer, prev_key

    op = (opcode & 0xF000) >> 12
    x = (opcode & 0x0F00) >> 8
    y = (opcode & 0x00F0) >> 4
    n = opcode & 0x000F
    kk = opcode & 0x00FF
    nnn = opcode & 0x0FFF
    key = get_sticky_key()
            
    #clear
    if opcode == 0x00E0:
        clear_display()
    #ret
    elif opcode == 0x00EE:
        PC = stack.pop()
    #jp
    elif op == 1:
        PC = nnn
    #call
    elif op == 2:
        stack.append(PC)
        PC = nnn
    #se
    elif op == 3:
        if V[x] == kk:
            PC += 2
    #sne
    elif op == 4:
        if V[x] != kk:
            PC += 2
    #se Vx Vy
    elif op == 5 and n == 0:
        if V[x] == V[y]:
            PC += 2
    #LD Vx byte
    elif op == 6:
        V[x] = kk
    #add Vx byte
    elif op == 7:
        V[x] = (V[x] + kk) & 0xFF
    #ld Vx Vy
    elif op == 8 and n == 0:
        V[x] = V[y]
    #or Vx Vy
    elif op == 8 and n == 1:
        V[x] |= V[y]
    #and Vx Vy
    elif op == 8 and n == 2:
        V[x] &= V[y]
    #xor Vx Vy
    elif op == 8 and n == 3:
        V[x] ^= V[y]
    #add Vx Vy
    elif op == 8 and n == 4:
        total = V[x] + V[y]
        V[0xF] = 1 if total > 0xFF else 0
        V[x] = total & 0xFF
    #sub Vx Vy
    elif op == 8 and n == 5:
        V[0xF] = 1 if V[x] >= V[y] else 0
        V[x] = (V[x] - V[y]) & 0xFF
    #shr Vx
    elif op == 8 and n == 6:
        V[0xF] = V[x] & 1
        V[x] >>= 1
    #subn Vx Vy
    elif op == 8 and n == 7:
        V[0xF] = 1 if V[y] >= V[x] else 0
        V[x] = (V[y] - V[x]) & 0xFF
    #shl Vx
    elif op == 8 and n == 0xE:
        V[0xF] = (V[x] & 0x80) >> 7
        V[x] = (V[x] << 1) & 0xFF
    #sne Vx Vy
    elif op == 9 and n == 0:
        if V[x] != V[y]:
            PC += 2
    #ld I addr
    elif op == 0xA:
        I = nnn
    #jp V0, addr
    elif op == 0xB:
        PC = nnn + V[0]
    #rnd Vx byte
    elif op == 0xC:
        V[x] = random.getrandbits(8) & kk
    #draw Vx Vy sprite
    elif op == 0xD:
        draw_sprite(V[x] % 64, V[y] % 32, n)
    #skip Vx
    elif op == 0xE:
        if kk == 0x9E:
            if key == V[x]:
                PC += 2
        elif kk == 0xA1:
            if key != V[x]:
                PC += 2
    #ld delays
    elif op == 0xF:
        if kk == 0x07:
            V[x] = delay_timer
        #ld Vx, K
        elif kk == 0x0A:
            key = get_keymap(True)
            if key is not None:
                V[x] = key
        #ld delay, Vx
        elif kk == 0x15:
            delay_timer = V[x]
        #ld sound, Vx
        elif kk == 0x18:
            sound_timer = V[x]
        #add Vx, I
        elif kk == 0x1E:
            I = (I + V[x]) & 0xFFF
        #ld Vx, [I]
        elif kk == 0x29:
            #i = location of sprite
            I = V[x] * 5
        elif kk == 0x33:
            #BCD
            memory[I] = V[x] // 100
            memory[I + 1] = (V[x] // 10) % 10
            memory[I + 2] = V[x] % 10
        elif kk == 0x55:
            for i in range(x + 1):
                memory[I + i] = V[i]
        elif kk == 0x65:
            for i in range(x + 1):
                V[i] = memory[I + i]

def run():
    global PC, delay_timer, sound_timer, draw_flag

    load_font()
    load_rom(ROM)
    print("I'm alive")
    last_time = time.ticks_ms()

    while not ti_system.escape():
        #batch
        for _ in range(INSTRS_PER_FRAME):
            opcode = (memory[PC] << 8) | memory[PC + 1]
            PC = (PC + 2) & 0xFFF
            execute(opcode)
            
            if draw_flag:
                render()
                draw_flag = False
            

        #render as soon as changed

        #update timers
        now = time.ticks_ms()
        if time.ticks_diff(now, last_time) >= 16:
            if delay_timer > 0:
                delay_timer -= 1
            if sound_timer > 0:
                sound_timer -= 1
            last_time = now

            if draw_flag:
                render()
                draw_flag = False
        # don't make the calculator overwork
        time.sleep(0.01)