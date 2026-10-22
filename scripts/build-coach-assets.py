from __future__ import annotations

import math
import shutil
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "coaches"
PUBLIC = ROOT / "public"
ANIMATIONS = PUBLIC / "animations"
CHARACTERS = PUBLIC / "characters"
SIZE = 420
STATIC_SIZE = 520
MOTION_BACKGROUND = (248, 244, 250, 255)

EXERCISES = [
    "march", "squat", "wide", "chair", "wall", "bird", "knee",
    "chest", "back", "calf", "core", "tilt", "cat", "heel-slide",
    "knee-fallout", "supine-march", "dead-bug", "glute-bridge",
    "step-up", "calf-raise", "side-plank-knees",
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
    "sabina-dynamic-sheet.png": [(0, 375), (420, 760), (795, 1145), (1185, 1536)],
    "sabina-upper-sheet.png": [(0, 360), (370, 760), (770, 1145), (1150, 1536)],
    "sabina-floor-sheet.png": [(0, 300), (320, 600), (620, 805), (825, 1024)],
    "sabina-diastasis-sheet.png": [(0, 410), (440, 690), (710, 1024)],
    "victor-key-motions-sheet.png": [
        (0, 325), (380, 715), (785, 900), (985, 1095), (1170, 1295), (1340, 1536)
    ],
}


MULTIFRAME_COMBINED = {
    "heel-slide": "heel-slide-4frames.png",
    "supine-march": "supine-march-4frames.png",
    "dead-bug": "dead-bug-4frames.png",
    "glute-bridge": "glute-bridge-4frames.png",
    "bird": "bird-dog-4frames.png",
    "wall": "wall-pushup-4frames.png",
    "squat": "squat-4frames.png",
    "step-up": "step-up-4frames.png",
    "calf-raise": "calf-raise-4frames.png",
    "side-plank-knees": "side-plank-knees-4frames.png",
}

MULTIFRAME_SEPARATE = {
    "core": {
        "sabina": "sabina-breathing-4frames.png",
        "victor": "victor-breathing-4frames.png",
    },
}

PHASES = {
    "core": ["PREPARA", "INHALA 360°", "EXHALA", "ACTIVA SUAVE"],
    "heel-slide": ["PREPARA", "DESLIZA", "EXTIENDE", "REGRESA"],
    "supine-march": ["PIES APOYADOS", "ELEVA UN PIE", "ALTERNA", "REGRESA"],
    "dead-bug": ["PREPARA", "BAJA EL TALÓN", "EXTIENDE EL BRAZO", "REGRESA"],
    "glute-bridge": ["PREPARA", "INICIA", "ELEVA LA PELVIS", "BAJA SUAVE"],
    "bird": ["CUATRO APOYOS", "EXTIENDE", "MANTÉN NIVEL", "REGRESA"],
    "wall": ["PREPARA", "ACÉRCATE", "FLEXIONA", "EMPUJA"],
    "squat": ["DE PIE", "CADERA ATRÁS", "BAJA CON CONTROL", "SUBE"],
    "step-up": ["PREPARA", "APOYA EL PIE", "SUBE", "BAJA CON CONTROL"],
    "calf-raise": ["TALONES ABAJO", "SUBE", "PUNTAS DE PIE", "BAJA LENTO"],
    "side-plank-knees": ["APOYA", "ELEVA", "ALINEA", "BAJA SUAVE"],
}

CUES = {
    "march": "ALTERNA LAS RODILLAS",
    "calf": "TALÓN TRASERO ABAJO",
    "core": "RESPIRA Y ACTIVA",
    "tilt": "BASCULA LA PELVIS",
    "heel-slide": "DESLIZA EL TALÓN",
    "knee-fallout": "ABRE SIN GIRAR LA PELVIS",
    "supine-march": "MARCHA SIN ARQUEAR",
    "dead-bug": "MUEVE UNA EXTREMIDAD",
    "glute-bridge": "ELEVA CON GLÚTEOS",
    "bird": "PELVIS ESTABLE",
    "wall": "CUERPO ALINEADO",
    "squat": "RODILLAS HACIA LOS PIES",
    "step-up": "TODA LA PLANTA APOYADA",
    "calf-raise": "SUBE Y BAJA CON CONTROL",
    "side-plank-knees": "HOMBRO · CADERA · RODILLA",
}

FONT_PATHS = [
    Path(r"C:\Windows\Fonts\seguisb.ttf"),
    Path(r"C:\Windows\Fonts\arialbd.ttf"),
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


def clean_cutout(image: Image.Image) -> Image.Image:
    """Remove generated glow and disconnected scraps before resizing a pose."""
    image = image.convert("RGBA")
    alpha = image.getchannel("A").point(
        lambda value: 0 if value < 78 else 255 if value > 218 else round((value - 78) * 255 / 140)
    )
    width, height = image.size
    mask = alpha.point(lambda value: 255 if value >= 28 else 0)
    pixels = mask.load()
    visited = bytearray(width * height)
    remove_boxes: list[tuple[int, int, int, int]] = []
    minimum_area = max(700, width * height // 240)

    for y in range(height):
        for x in range(width):
            index = y * width + x
            if visited[index] or not pixels[x, y]:
                continue
            queue = deque([(x, y)])
            visited[index] = 1
            count = 0
            left = right = x
            top = bottom = y
            while queue:
                current_x, current_y = queue.popleft()
                count += 1
                left = min(left, current_x)
                right = max(right, current_x)
                top = min(top, current_y)
                bottom = max(bottom, current_y)
                for next_x, next_y in ((current_x - 1, current_y), (current_x + 1, current_y), (current_x, current_y - 1), (current_x, current_y + 1)):
                    if 0 <= next_x < width and 0 <= next_y < height:
                        next_index = next_y * width + next_x
                        if not visited[next_index] and pixels[next_x, next_y]:
                            visited[next_index] = 1
                            queue.append((next_x, next_y))
            if count < minimum_area:
                remove_boxes.append((max(0, left - 3), max(0, top - 3), min(width, right + 4), min(height, bottom + 4)))

    if remove_boxes:
        draw = ImageDraw.Draw(alpha)
        for box in remove_boxes:
            draw.rectangle(box, fill=0)
    image.putalpha(alpha)
    return image


def normalize(image: Image.Image, size: int, top_space: int = 12, horizontal_padding: int = 9) -> Image.Image:
    image = clean_cutout(image)
    alpha = image.getchannel("A")
    strong = alpha.point(lambda value: 255 if value >= 36 else 0)
    bounds = strong.getbbox() or alpha.getbbox()
    if bounds:
        image = image.crop(bounds)
    max_width = size - horizontal_padding * 2
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


def on_motion_background(image: Image.Image) -> Image.Image:
    background = Image.new("RGBA", image.size, MOTION_BACKGROUND)
    background.alpha_composite(image)
    return background


def pose_sequence(first: Image.Image, second: Image.Image, hold: int = 9) -> list[Image.Image]:
    """Show two unambiguous key poses without inventing intermediate anatomy."""
    first = on_motion_background(first)
    second = on_motion_background(second)
    return [first.copy() for _ in range(hold)] + [second.copy() for _ in range(hold)]


def single_pose_sequence(pose: Image.Image, frames: int = 18) -> list[Image.Image]:
    pose = on_motion_background(pose)
    return [pose.copy() for _ in range(frames)]


def exercise_frames(exercise: str, start: Image.Image, end: Image.Image) -> list[Image.Image]:
    if exercise == "march":
        return pose_sequence(start, ImageOps.mirror(start))
    if exercise in {"calf", "core"}:
        return single_pose_sequence(end)
    return pose_sequence(start, end)


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


def phase_label(draw: ImageDraw.ImageDraw, message: str) -> None:
    label_font = font(14)
    box = draw.textbbox((0, 0), message, font=label_font)
    label_width = box[2] - box[0] + 24
    draw.rounded_rectangle(((SIZE - label_width) // 2, SIZE - 39, (SIZE + label_width) // 2, SIZE - 9), radius=14, fill=(255, 255, 255, 238))
    draw.text((SIZE // 2, SIZE - 24), message, font=label_font, fill=(25, 28, 48, 255), anchor="mm")


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
    if exercise in PHASES:
        phase_index = min(3, index * 4 // total)
        phase_label(draw, PHASES[exercise][phase_index])
    pulse = 150 + round(90 * (0.5 + 0.5 * math.sin(index / total * math.tau)))
    orange = (255, 120, 65, pulse)
    cyan = (39, 184, 176, pulse)

    if exercise == "march":
        if index < total / 2:
            arrow(draw, (292, 350), (292, 282), cyan)
        else:
            arrow(draw, (128, 350), (128, 282), orange)
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
        phase_label(draw, phase)
    elif exercise == "tilt":
        if index < total / 2:
            draw.line((185, 291, 275, 291), fill=cyan, width=8)
            phase_label(draw, "PELVIS NEUTRA")
        else:
            draw.line((185, 302, 275, 279), fill=orange, width=8)
            draw.arc((175, 245, 305, 350), start=195, end=335, fill=orange, width=7)
            arrow(draw, (292, 315), (310, 292), orange)
            phase_label(draw, "ACERCA LA CINTURA AL SUELO")
    elif exercise == "heel-slide":
        arrow(draw, (235, 370), (360, 370), cyan)
        arrow(draw, (360, 392), (235, 392), orange)
        phase_label(draw, "FLEXIONA" if index < total / 2 else "DESLIZA SIN ARQUEAR")
    elif exercise == "knee-fallout":
        if index < total / 2:
            draw.line((300, 220, 300, 350), fill=orange, width=5)
            phase_label(draw, "RODILLA AL CENTRO")
        else:
            draw.arc((220, 210, 382, 390), start=250, end=350, fill=cyan, width=8)
            arrow(draw, (367, 330), (379, 359), cyan)
            phase_label(draw, "ABRE SIN GIRAR LA PELVIS")
    return result


def grid_cell(sheet: Image.Image, row: int, rows: int, column: int, columns: int) -> Image.Image:
    width, height = sheet.size
    x0 = round(column * width / columns) + 3
    x1 = round((column + 1) * width / columns) - 3
    y0 = round(row * height / rows) + 3
    y1 = round((row + 1) * height / rows) - 3
    return sheet.crop((x0, y0, x1, y1)).convert("RGBA")


def fit_grid_frame(image: Image.Image, size: int = SIZE) -> Image.Image:
    image = image.convert("RGBA")
    max_width, max_height = size - 16, size - 58
    ratio = min(max_width / image.width, max_height / image.height)
    resized = image.resize((round(image.width * ratio), round(image.height * ratio)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), MOTION_BACKGROUND)
    canvas.alpha_composite(resized, ((size - resized.width) // 2, 44 + (max_height - resized.height) // 2))
    return canvas


def multiframe_raw(exercise: str, coach: str) -> list[Image.Image] | None:
    if exercise in MULTIFRAME_SEPARATE:
        sheet = Image.open(SOURCE / MULTIFRAME_SEPARATE[exercise][coach]).convert("RGBA")
        return [grid_cell(sheet, row, 2, column, 2) for row in range(2) for column in range(2)]
    filename = MULTIFRAME_COMBINED.get(exercise)
    if not filename:
        return None
    sheet = Image.open(SOURCE / filename).convert("RGBA")
    row = 0 if coach == "sabina" else 1
    return [grid_cell(sheet, row, 2, column, 4) for column in range(4)]


def multiframe_sequence(raw_frames: list[Image.Image], hold: int = 5) -> list[Image.Image]:
    frames = [fit_grid_frame(frame) for frame in raw_frames]
    return [frame.copy() for frame in frames for _ in range(hold)]


def gif_palette(image: Image.Image) -> Image.Image:
    return on_motion_background(image).convert("RGB").quantize(
        colors=256,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.FLOYDSTEINBERG,
    )


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
        disposal=1,
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

    for exercise in EXERCISES:
        raw_frames = multiframe_raw(exercise, "sabina")
        if raw_frames:
            frames = multiframe_sequence(raw_frames)
            save_gif(frames, ANIMATIONS / "sabina" / f"{exercise}.gif", exercise)
            save_static(fit_grid_frame(raw_frames[2], STATIC_SIZE), CHARACTERS / "sabina" / f"{exercise}.webp")
            continue
        start_raw, end_raw = pairs[exercise]
        padding = 38 if exercise in {"core", "tilt", "heel-slide", "knee-fallout"} else 16
        start = normalize(start_raw, SIZE, 52, padding)
        end = normalize(end_raw, SIZE, 52, padding)
        frames = exercise_frames(exercise, start, end)
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
    for exercise in EXERCISES:
        raw_frames = multiframe_raw(exercise, "victor")
        if raw_frames:
            frames = multiframe_sequence(raw_frames)
            save_static(fit_grid_frame(raw_frames[2], STATIC_SIZE), destination_characters / f"{exercise}.webp")
            save_gif(frames, destination_animations / f"{exercise}.gif", exercise)
            continue
        if exercise in overrides:
            start_raw, end_raw = overrides[exercise]
            padding = 38 if exercise in {"core", "tilt", "heel-slide", "knee-fallout"} else 16
            start = normalize(start_raw, SIZE, 52, padding)
            end = normalize(end_raw, SIZE, 52, padding)
            frames = exercise_frames(exercise, start, end)
            static_raw = end_raw if exercise != "march" else start_raw
            save_static(normalize(static_raw, STATIC_SIZE, 12), destination_characters / f"{exercise}.webp")
        else:
            first_raw, second_raw = load_existing_gif(source_animations / f"{exercise}.gif")
            first = normalize(first_raw, SIZE, 52)
            second = normalize(second_raw, SIZE, 52)
            frames = pose_sequence(first, second)
            shutil.copy2(source_characters / f"{exercise}.webp", destination_characters / f"{exercise}.webp")
        save_gif(frames, destination_animations / f"{exercise}.gif", exercise)


def main() -> None:
    build_sabina()
    build_victor()
    print(f"Generated {len(EXERCISES)} Sabina GIFs and {len(EXERCISES)} Victor GIFs.")


if __name__ == "__main__":
    main()
