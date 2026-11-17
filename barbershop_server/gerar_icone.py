import zlib
import struct

w, h = 512, 512
linhas = []

for y in range(h):
    linha = bytearray([0])
    for x in range(w):
        borda = x < 36 or x >= w - 36 or y < 36 or y >= h - 36
        centro = 170 <= x <= 342 and 170 <= y <= 342
        if borda or centro:
            linha.extend([0, 245, 212, 255])  # Verde-água neon (#00F5D4)
        else:
            linha.extend([18, 18, 20, 255])   # Fundo escuro (#121214)
    linhas.append(bytes(linha))

raw = b"".join(linhas)

def chunk(tag, data):
    return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xffffffff)

png = (
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack("!IIBBBBB", w, h, 8, 6, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(raw))
    + chunk(b"IEND", b"")
)

from pathlib import Path

destino = Path(__file__).resolve().parent.parent / "templates" / "icone_app.png"
with open(destino, "wb") as f:
    f.write(png)

print("ICONE OFICIAL 512x512 CRIADO COM SUCESSO EM:", destino)

