SBOX = [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]

def compute_ddt(sbox):
    n = len(sbox)
    ddt = [[0]*n for _ in range(n)]
    for x in range(n):
        for dx in range(n):
            x2 = x ^ dx
            dy = sbox[x] ^ sbox[x2]
            ddt[dx][dy] += 1
    return ddt

ddt = compute_ddt(SBOX)

print("DDT (rows=ΔIN, cols=ΔOUT):")
print("     " + "  ".join(f"{j:X}" for j in range(16)))
for i, row in enumerate(ddt):
    print(f"{i:X}  | " + "  ".join(f"{v:2d}" for v in row))

max_val = max(ddt[i][j] for i in range(1,16) for j in range(1,16))
print(f"\nMax non-trivial DDT entry: {max_val}")
print(f"DPmax = {max_val}/16 = 2^(-{int(16/max_val).bit_length()-1}... = {max_val/16:.4f}")