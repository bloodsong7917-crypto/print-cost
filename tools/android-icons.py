# Кладёт иконку приложения в ресурсы Android-проекта (путь к android/ — первым аргументом).
import sys, os, zlib, struct
BG, FG, NZ = (10, 108, 108), (255, 255, 255), (229, 161, 82)
BARS = [(0.24, 0.76, 0.62, 0.70), (0.30, 0.70, 0.50, 0.58), (0.36, 0.64, 0.38, 0.46)]

def png(n, k=1.0):
    """k < 1 сжимает рисунок к центру (для адаптивной иконки с обрезкой по маске)."""
    f = lambda v: 0.5 + (v - 0.5) * k
    rows = []
    for y in range(n):
        fy = 0.5 + ((y + 0.5) / n - 0.5) / k
        row = bytearray(bytes(BG) * n)
        for x0, x1, y0, y1 in BARS:
            if y0 <= fy < y1:
                i0, i1 = int(f(x0) * n), int(f(x1) * n)
                row[i0 * 3:i1 * 3] = bytes(FG) * (i1 - i0)
        if 0.22 <= fy < 0.34:
            h = (0.34 - fy) / 0.12 * 0.07 + 0.012
            i0, i1 = int(f(0.5 - h) * n), int(f(0.5 + h) * n)
            row[i0 * 3:i1 * 3] = bytes(NZ) * (i1 - i0)
        rows.append(b"\x00" + bytes(row))
    ch = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    return (b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0))
            + ch(b"IDAT", zlib.compress(b"".join(rows), 9)) + ch(b"IEND", b""))

res = os.path.join(sys.argv[1], "app", "src", "main", "res")
for d, s in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
    m = os.path.join(res, "mipmap-" + d)
    open(os.path.join(m, "ic_launcher.png"), "wb").write(png(s))
    open(os.path.join(m, "ic_launcher_round.png"), "wb").write(png(s, 0.8))
    open(os.path.join(m, "ic_launcher_foreground.png"), "wb").write(png(s * 108 // 48, 0.75))
