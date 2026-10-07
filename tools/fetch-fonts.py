# Скачивает шрифты Google Fonts в www/fonts, чтобы приложение выглядело одинаково без интернета.
import re, os, urllib.request
URL = "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Onest:wght@400;500;600;700&family=Unbounded:wght@500;700&display=swap"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
KEEP = {"cyrillic", "latin"}
out = os.path.join(os.path.dirname(__file__), "..", "www", "fonts")
os.makedirs(out, exist_ok=True)
css = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": UA})).read().decode()
res, seen = [], {}
for subset, block in re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, re.S):
    if subset not in KEEP: continue
    url = re.search(r"url\((https://[^)]+)\)", block).group(1)
    if url not in seen:
        fam = re.search(r"font-family: '([^']+)'", block).group(1).replace(" ", "")
        seen[url] = "%s-%s-%d.woff2" % (fam, subset, len(seen))
        open(os.path.join(out, seen[url]), "wb").write(urllib.request.urlopen(url).read())
    res.append(block.replace(url, seen[url]))
open(os.path.join(out, "fonts.css"), "w").write("\n".join(res) + "\n")
print(len(seen), "files")
