#!/usr/bin/env python3
# 莫名知道：每日動畫知識 Shorts（簡易免費版）
import os, math, subprocess, textwrap
from datetime import date
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 24
OUT = "output"
os.makedirs(OUT, exist_ok=True)

# 每天依日期輪替一則已整理的常識題材；不是即時新聞或即時網路查證。
FACTS = [
    ("為什麼天空是藍色的？", "陽光其實包含各種顏色。", "空氣分子更容易散射藍光，", "所以我們從四面八方看到藍色天空。", "這種現象叫做「瑞利散射」。"),
    ("章魚有幾顆心臟？", "答案是：三顆！", "兩顆把血液送往鰓，", "另一顆把血液送到全身。", "而且章魚的血液是偏藍色的。"),
    ("蜂蜜為什麼不容易壞？", "蜂蜜含水量低、糖分很高。", "這種環境不利許多微生物生長，", "再加上蜂蜜偏酸，", "因此保存得當時可以放很久。"),
    ("人為什麼會起雞皮疙瘩？", "這是身體保留下來的反射。", "寒冷或情緒激動時，", "毛囊旁的小肌肉收縮，", "讓毛髮豎起，皮膚就像雞皮一樣。"),
    ("海水為什麼是鹹的？", "雨水和河流會慢慢溶解岩石中的礦物質。", "這些溶解的離子一路流進海洋，", "水分蒸發後，鹽分卻留了下來。", "經過漫長時間，海水就帶有鹹味。"),
    ("熱水一定比冷水先結冰嗎？", "不一定，但有時會出現這種情況。", "某些條件下，熱水可能比冷水更快結冰，", "這種現象稱為「姆潘巴效應」。", "它受容器、蒸發和水中氣體等因素影響。"),
    ("指紋為什麼每個人都不同？", "指紋在胎兒發育時逐漸形成。", "基因會影響大致形狀，", "但子宮內的壓力和微小環境差異，", "讓每個人的紋路都具有獨特性。"),
]
fact = FACTS[(date.today() - date(2025, 1, 1)).days % len(FACTS)]
title, *lines = fact

FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if not os.path.exists(FONT_PATH):
    raise RuntimeError("找不到中文字型，請確認 workflow 有安裝 fonts-noto-cjk")

def font(size):
    return ImageFont.truetype(FONT_PATH, size, index=0)

def wrap(draw, text, f, max_width):
    out, line = [], ""
    for ch in text:
        test = line + ch
        if draw.textbbox((0, 0), test, font=f)[2] <= max_width:
            line = test
        else:
            if line: out.append(line)
            line = ch
    if line: out.append(line)
    return out

def make_frame(t, total):
    im = Image.new("RGB", (W, H), (10, 16, 35))
    d = ImageDraw.Draw(im)
    # moving decorative rings and dots
    for i in range(7):
        x = int((i * 137 + t * (24 + i * 3)) % (W + 160)) - 80
        y = int(170 + (i % 3) * 390 + 22 * math.sin(t * 1.3 + i))
        r = 18 + (i * 7) % 28
        d.ellipse((x-r, y-r, x+r, y+r), outline=(35, 95, 150), width=3)
    d.rounded_rectangle((42, 55, 678, 1225), radius=34, outline=(54, 112, 170), width=3)
    d.text((72, 82), "莫名知道  •  每日一個冷知識", font=font(25), fill=(125, 220, 255))
    # progress indicator
    d.rounded_rectangle((72, 137, 648, 147), radius=5, fill=(35, 48, 75))
    d.rounded_rectangle((72, 137, 72 + int(576 * t / total), 147), radius=5, fill=(70, 205, 220))
    # title and scene text
    scene = min(5, int(t // 4))
    if scene == 0:
        headline = title
        body = "你知道嗎？"
    elif scene == 5:
        headline = "你還知道哪些？"
        body = "留言分享，追蹤「莫名知道」"
    else:
        headline = f"冷知識 0{scene}"
        body = lines[scene-1] if scene-1 < len(lines) else lines[-1]
    hf, bf = font(48), font(39)
    y = 390 if scene == 0 else 420
    for ln in wrap(d, headline, hf, 540):
        box = d.textbbox((0,0), ln, font=hf)
        d.text(((W-(box[2]-box[0]))/2, y), ln, font=hf, fill=(255, 230, 120), stroke_width=2, stroke_fill=(20,30,55))
        y += 72
    y += 45
    for ln in wrap(d, body, bf, 530):
        box = d.textbbox((0,0), ln, font=bf)
        d.text(((W-(box[2]-box[0]))/2, y), ln, font=bf, fill=(245, 248, 255))
        y += 62
    d.text((72, 1160), "知識內容為一般科普整理", font=font(20), fill=(155, 175, 200))
    return im

duration = 24
raw = os.path.join(OUT, "frames")
os.makedirs(raw, exist_ok=True)
for n in range(duration * FPS):
    frame = make_frame(n / FPS, duration)
    frame.save(os.path.join(raw, f"{n:05d}.png"))

today = date.today().strftime("%Y%m%d")
video = os.path.join(OUT, f"moming_shorts_{today}.mp4")
subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{raw}/%05d.png",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-movflags", "+faststart", video
], check=True)
print("Created:", video)
