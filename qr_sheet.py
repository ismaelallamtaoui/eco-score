from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "site_build"
QR_DIR = BUILD / "qr"
OUT_DIR = ROOT / "artifacts"
OUT_DIR.mkdir(exist_ok=True, parents=True)

DPI = 300
A4_W, A4_H = int(8.27 * DPI), int(11.69 * DPI)
MARGIN = int(0.5 * DPI)
COLS, ROWS = 3, 3
GUTTER = int(0.25 * DPI)

def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def make_pages():
    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    items = manifest["records"]
    qr_map = {(QR_DIR / f"{it['slug']}.png"): it for it in items}
    qr_paths = list(qr_map.keys())

    pages = []
    font_title = get_font(26)
    font_label = get_font(20)

    cell_w = (A4_W - 2*MARGIN - (COLS-1)*GUTTER) // COLS
    cell_h = (A4_H - 2*MARGIN - (ROWS-1)*GUTTER) // ROWS

    for group in chunk(qr_paths, COLS*ROWS):
        page = Image.new("RGB", (A4_W, A4_H), "white")
        draw = ImageDraw.Draw(page)
        title = "QR produits — Éco-score"
        draw.text((MARGIN, MARGIN - int(0.3*DPI)), title, fill="black", font=font_title)

        for idx, qr_path in enumerate(group):
            r = idx // COLS
            c = idx % COLS
            x = MARGIN + c*(cell_w + GUTTER)
            y = MARGIN + r*(cell_h + GUTTER) + int(0.2*DPI)

            qr = Image.open(qr_path).convert("RGB")
            max_qr = min(cell_w, cell_h - int(0.6*DPI))
            qr = qr.resize((max_qr, max_qr), Image.NEAREST)
            page.paste(qr, (x + (cell_w - max_qr)//2, y))

            item = qr_map[qr_path]
            label = f"{item['name']} — {item['grade']} ({item['score']})"
            draw.text((x + int(0.05*DPI), y + max_qr + int(0.15*DPI)), label, fill="black", font=font_label)

        pages.append(page)

    return pages

def save_pdf(pages, dest):
    if not pages:
        raise SystemExit("No QR pages to save")
    pages[0].save(dest, save_all=True, append_images=pages[1:], resolution=DPI)

if __name__ == "__main__":
    pages = make_pages()
    out_pdf = OUT_DIR / "qr_sheets_a4.pdf"
    save_pdf(pages, out_pdf)
    print(f"Wrote {out_pdf}")
