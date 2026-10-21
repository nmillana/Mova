from __future__ import annotations

import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "coaches"
PUBLIC = ROOT / "public"
ANIMATIONS = PUBLIC / "animations"
CHARACTERS = PUBLIC / "characters"
SIZE = 420
STATIC_SIZE = 520

EXERCISES = [
    "march", "squat", "wide", "chair", "wall", "bird", "knee",
    "chest", "back", "calf", "core", "tilt", "cat", "heel-slide",
    "knee-fallout",
]

SABINA_SHEETS = {
    "sabina-dynamic-sheet.png": (4, ["march", "squat", "chair", "wide"]),
    "sabina-upper-sheet.png": (4, ["wall", "chest", "back", "calf"]),
    "sabina-floor-sheet.png": (4, ["bird", "knee", "core", "tilt"]),
    "sabina-diastasis-sheet.png": (3, ["cat", "heel-slide", "knee-fallout"]),
}

VICTOR_SHEET = (
    "victor-key-motions-sheet.png",
    6,
    ["march", "calf", "core", "tilt", "heel-slide", "knee-fallout"],
)

SHEET_BANDS = {
    "sabina-dynamic-sheet.png": [(0, 375), (420, 760), (810, 1145), (1210, 1536)],
    "sabina-upper-sheet.png": [(0, 380), (420, 760), (810, 1145), (1210, 1536)],
    "sabina-floor-sheet.png": [(0, 300), (320, 600), (620, 805), (825, 1024)],
    "sabina-diastasis-sheet.png": [(0, 410), (440, 690), (710, 1024)],
    "victor-key-motions-sheet.png": [
        (0, 325), (380, 715), (785, 900), (985, 1095), (1170, 1295), (1340, 1536)
    ],
}

CUES = {
    "march": "ALTERNA LAS RODILLAS",
    "calf": "TALÓN TRASERO ABAJO",
    "core": "RESPIRA Y ACTIVA",
    "tilt": "BASCULA LA PELVIS",
    "heel-slide": "DESLIZA EL TALÓN",
    "knee-fallout": "ABRE SIN GIRAR LA PELVIS",
}

FONT_PATHS = [
    Path(r"C:WindowsFontsseguisb.ttf"),
    Path(r"C:WindowsFontsarialbd.ttf"),
]


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_PATHS:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def crop_cell(sheet: Image.Image, row: int, rows: int, column: int, top_trim: float = 0) -> Image.Image:
    width, height = sheet.size
    x0 = round(column * width / 2)
    x1 = round((column + 1) * width / 2)
    y0 = round(row * height / rows)
    y1 = round((row + 1) * height / rows)
    if row > 0 and top_trim:
        y0 += round((y1 - y0) * top_trim)
    return sheet.crop((x0, y0, x1, y1)).convert("RGBA")


def normalize(image: Image.Image, size: int, top_space: int = 12) -> Image.Image:
    image = image.convert("RGBA")
    alpha = image.getchannel("A")
    strong = alpha.point(lambda value: 255 if value >= 36 else 0)
    bounds = strong.getbbox() or alpha.getbbox()
    if bounds:
        image = image.crop(bounds)
    max_width = size - 18
    max_height = size - top_space - 12
    ratio = min(max_width / image.width, max_height / image.height)
    image = image.resize(
        (max(1, round(image.width * ratio)), max(1, round(image.height * ratio))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - image.width) // 2
    y = top_space + max(0, (max_height - image.height) // 2)
    canvas.alpha_composite(image, (x, y))
    return canvas


def ease(value: float) -> float:
    return (1 - math.cos(math.pi * value)) / 2


def transition(first: Image.Image, second: Image.Image, steps: int = 7) -> list[Image.Image]:
    forward = [first.copy(), first.copy()]
    for index in range(1, steps):
        forward.append(Image.blend(first, second, ease(index / steps)))
    forward.extend([second.copy(), second.copy(), second.copy()])
    backward = [Image.blend(second, first, ease(index / steps)) for index in range(1, steps)]
    return forward + backward + [first.copy()]


def march_transition(action: Image.Image, neutral: Image.Image) -> list[Image.Image]:
    right = ImageOps.mirror(action)
    frames: list[Image.Image] = []
    poses = [action, neutral, right, neutral, action]
    for start, end in zip(poses, poses[1:]):
        for index in range(4):
            frames.append(Image.blend(start, end, ease(index / 4)))
    frames.extend([action.copy(), action.copy()])
    return frames


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int, int], width: int = 7) -> None:
    draw.line((start, end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 16
    wing = 0.65
    points = [
        end,
        (round(end[0] - length * math.cos(angle - wing)), round(end[1] - length * math.sin(angle - wing))),
        (round(end[0] - length * math.cos(angle + wing)), round(end[1] - length * math.sin(angle + wing))),
    ]
    draw.polygon(points, fill=color)


def add_cue(image: Image.Image, exercise: str, index: int, total: int) -> Image.Image:
    if exercise not in CUES:
        return image
    result = image.copy()
    draw = ImageDraw.Draw(result, "RGBA")
    label = CUES[exercise]
    label_font = font(17)
    box = draw.textbbox((0, 0), label, font=label_font)
    width = box[2] - box[0] + 28
    draw.rounded_rectangle(((SIZE - width) // 2, 8, (SIZE + width) // 2, 41), radius=16, fill=(255, 255, 255, 235))
    draw.text((SIZE // 2, 24), label, font=label_font, fill=(25, 28, 48, 255), anchor="mm")
    pulse = 150 + round(90 * (0.5 + 0.5 * math.sin(index / total * math.tau)))
    orange = (255, 120, 65, pulse)
    cyan = (39, 184, 176, pulse)

    if exercise == "march":
        arrow(draw, (125, 345), (125, 285), orange)
        arrow(draw, (295, 345), (295, 285), cyan)
    elif exercise == "calf":
        arrow(draw, (120, 340), (120, 395), orange)
        draw.ellipse((94, 387, 146, 407), outline=(255, 120, 65, pulse), width=6)
    elif exercise == "core":
        first_half = index < total / 2
        if first_half:
            arrow(draw, (210, 270), (155, 270), cyan)
            arrow(draw, (210, 310), (155, 310), cyan)
            arrow(draw, (300, 270), (355, 270), cyan)
            arrow(draw, (300, 310), (355, 310), cyan)
            phase = "INHALA · ABRE COSTILLAS"
        else:
            arrow(draw, (150, 290), (215, 290), orange)
            arrow(draw, (365, 290), (300, 290), orange)
            phase = "EXHALA · OMBLIGO SUAVE HACIA DENTRO"
        small = font(14)
        phase_box = draw.textbbox((0, 0), phase, font=small)
        phase_width = phase_box[2] - phase_box[0] + 24
        draw.rounded_rectangle(((SIZE - phase_width) // 2, SIZE - 39, (SIZE + phase_width) // 2, SIZE - 9), radius=14, fill=(255, 255, 255, 235))
        draw.text((SIZE // 2, SIZE - 24), phase, font=small, fill=(25, 28, 48, 255), anchor="mm")
    elif exercise == "tilt":
        draw.arc((165, 220, 345, 395), start=195, end=335, fill=orange, width=8)
        arrow(draw, (330, 347), (349, 323), orange)
    elif exercise == "heel-slide":
        arrow(draw, (235, 370), (360, 370), cyan)
        arrow(draw, (360, 392), (235, 392), orange)
    elif exercise == "knee-fallout":
        draw.arc((220, 210, 382, 390), start=250, end=350, fill=cyan, width=8)
        arrow(draw, (367, 330), (379, 359), cyan)
    return result


def gif_palette(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    palette = image.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    transparent = alpha.point(lambda value: 255 if value <= 12 else 0)
    palette.paste(255, mask=transparent)
    palette.info["transparency"] = 255
    return palette


def save_gif(frames: list[Image.Image], path: Path, exercise: str) -> None:
    annotated = [add_cue(frame, exercise, index, len(frames)) for index, frame in enumerate(frames)]
    paletted = [gif_palette(frame) for frame in annotated]
    path.parent.mkdir(parents=True, exist_ok=True)
    paletted[0].save(
        path,
        save_all=True,
        append_images=paletted[1:],
        duration=105,
        loop=0,
        disposal=2,
        transparency=255,
        optimize=True,
    )


def save_static(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "WEBP", quality=88, method=6)


def extract_sheet(filename: str, rows: int, exercises: list[str]) -> dict[str, tuple[Image.Image, Image.Image]]:
    sheet = Image.open(SOURCE / filename).convert("RGBA")
    bands = SHEET_BANDS.get(filename)
    if bands:
        width, _ = sheet.size
        return {
            exercise: (
                sheet.crop((0, bands[row][0], width // 2, bands[row][1])).convert("RGBA"),
                sheet.crop((width // 2, bands[row][0], width, bands[row][1])).convert("RGBA"),
            )
            for row, exercise in enumerate(exercises)
        }
    return {
        exercise: (
            crop_cell(sheet, row, rows, 0),
            crop_cell(sheet, row, rows, 1),
        )
        for row, exercise in enumerate(exercises)
    }


def build_sabina() -> None:
    pairs: dict[str, tuple[Image.Image, Image.Image]] = {}
    for filename, (rows, exercises) in SABINA_SHEETS.items():
        pairs.update(extract_sheet(filename, rows, exercises))

    action_march = normalize(pairs["march"][0], SIZE, 52)
    neutral_march = normalize(pairs["squat"][0], SIZE, 52)

    for exercise in EXERCISES:
        start_raw, end_raw = pairs[exercise]
        start = normalize(start_raw, SIZE, 52)
        end = normalize(end_raw, SIZE, 52)
        frames = march_transition(action_march, neutral_march) if exercise == "march" else transition(start, end)
        save_gif(frames, ANIMATIONS / "sabina" / f"{exercise}.gif", exercise)
        static = normalize(end_raw if exercise != "march" else start_raw, STATIC_SIZE, 12)
        save_static(static, CHARACTERS / "sabina" / f"{exercise}.webp")


def load_existing_gif(path: Path) -> tuple[Image.Image, Image.Image]:
    source = Image.open(path)
    frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(source)]
    if len(frames) == 1:
        frames.append(frames[0].copy())
    return frames[0], frames[-1]


def build_victor() -> None:
    source_characters = CHARACTERS
    source_animations = ANIMATIONS
    destination_characters = CHARACTERS / "victor"
    destination_animations = ANIMATIONS / "victor"
    destination_characters.mkdir(parents=True, exist_ok=True)
    destination_animations.mkdir(parents=True, exist_ok=True)

    filename, rows, exercises = VICTOR_SHEET
    overrides = extract_sheet(filename, rows, exercises)
    march_action = normalize(overrides["march"][0], SIZE, 52)
    neutral_raw = Image.open(source_characters / "chest.webp").convert("RGBA")
    march_neutral = normalize(neutral_raw, SIZE, 52)

    for exercise in EXERCISES:
        if exercise in overrides:
            start_raw, end_raw = overrides[exercise]
            start = normalize(start_raw, SIZE, 52)
            end = normalize(end_raw, SIZE, 52)
            frames = march_transition(march_action, march_neutral) if exercise == "march" else transition(start, end)
            static_raw = end_raw if exercise != "march" else start_raw
            save_static(normalize(static_raw, STATIC_SIZE, 12), destination_characters / f"{exercise}.webp")
        else:
            first_raw, second_raw = load_existing_gif(source_animations / f"{exercise}.gif")
            first = normalize(first_raw, SIZE, 52)
            second = normalize(second_raw, SIZE, 52)
            frames = transition(first, second)
            shutil.copy2(source_characters / f"{exercise}.webp", destination_characters / f"{exercise}.webp")
        save_gif(frames, destination_animations / f"{exercise}.gif", exercise)


def main() -> None:
    build_sabina()
    build_victor()
    print(f"Generated {len(EXERCISES)} Sabina GIFs and {len(EXERCISES)} Victor GIFs.")


if __name__ == "__main__":
    main()
