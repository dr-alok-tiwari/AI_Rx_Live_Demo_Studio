"""Build print and social flyers for the AI Rx programme.

The photographic hero is a project-owned, text-free generated asset. All copy,
branding, and programme information are typeset here so that the deliverables
remain reproducible and free from generated lettering.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
BRANDING = ROOT / "assets" / "branding"
MARKETING = ROOT / "assets" / "marketing"

SOURCE_LOGO = BRANDING / "ks_publication_pathway_logo.jpeg"
CROPPED_LOGO = BRANDING / "ks_publication_pathway_logo_cropped.png"
HERO = MARKETING / "AI_Rx_Flyer_Hero_v2.png"
PRINT_PNG = MARKETING / "AI_Rx_Advanced_AI_for_Doctors_Flyer_v2.png"
PRINT_PDF = MARKETING / "AI_Rx_Advanced_AI_for_Doctors_Flyer_v2.pdf"
SOCIAL_PNG = MARKETING / "AI_Rx_Advanced_AI_for_Doctors_Social_v2.png"

NAVY = "#061923"
NAVY_2 = "#0A2A38"
TEAL = "#18B9AD"
TEAL_DARK = "#0F766E"
AMBER = "#F59E0B"
CREAM = "#FFF9EC"
INK = "#0B2632"
MUTED = "#49646D"
WHITE = "#FFFFFF"

FONT_REGULAR = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
)
FONT_BOLD = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
)


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    for candidate in FONT_BOLD if bold else FONT_REGULAR:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    raise FileNotFoundError("A supported TrueType font was not found.")


def _crop_logo() -> Image.Image:
    """Crop surplus white space while preserving a generous logo margin."""

    image = Image.open(SOURCE_LOGO).convert("RGB")
    white = Image.new("RGB", image.size, WHITE)
    difference = ImageChops.difference(image, white).convert("L")
    difference = difference.point(lambda value: 255 if value > 18 else 0)
    bbox = difference.getbbox()
    if bbox:
        left, top, right, bottom = bbox
        pad_x = max(18, int((right - left) * 0.045))
        pad_y = max(18, int((bottom - top) * 0.09))
        bbox = (
            max(0, left - pad_x),
            max(0, top - pad_y),
            min(image.width, right + pad_x),
            min(image.height, bottom + pad_y),
        )
        image = image.crop(bbox)
    CROPPED_LOGO.parent.mkdir(parents=True, exist_ok=True)
    image.save(CROPPED_LOGO, format="PNG", optimize=True)
    return image


def _cover(image: Image.Image, width: int, height: int, *, focus_x: float = 0.5, focus_y: float = 0.5) -> Image.Image:
    scale = max(width / image.width, height / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, min(resized.width - width, round((resized.width - width) * focus_x)))
    top = max(0, min(resized.height - height, round((resized.height - height) * focus_y)))
    return resized.crop((left, top, left + width, top + height))


def _contain(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = min(width / image.width, height / image.height)
    return image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if draw.textlength(candidate, font=font) <= max_width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    *,
    spacing: int,
) -> int:
    x, y = xy
    lines = _wrap(draw, text, font, max_width)
    line_height = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height + spacing
    return y


def _paste_logo(canvas_image: Image.Image, logo: Image.Image, box: tuple[int, int, int, int], *, radius: int) -> None:
    x, y, width, height = box
    card = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    fitted = _contain(logo, width - 44, height - 36)
    card.alpha_composite(fitted.convert("RGBA"), ((width - fitted.width) // 2, (height - fitted.height) // 2))
    canvas_image.paste(card.convert("RGB"), (x, y), mask)


def _gradient_overlay(size: tuple[int, int], start_alpha: int, end_alpha: int, *, horizontal: bool = True) -> Image.Image:
    width, height = size
    overlay = Image.new("RGBA", size)
    draw = ImageDraw.Draw(overlay)
    steps = width if horizontal else height
    for position in range(steps):
        ratio = position / max(1, steps - 1)
        alpha = round(start_alpha + (end_alpha - start_alpha) * ratio)
        if horizontal:
            draw.line((position, 0, position, height), fill=(4, 19, 28, alpha))
        else:
            draw.line((0, position, width, position), fill=(4, 19, 28, alpha))
    return overlay


def _feature_card(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    number: str,
    title: str,
    body: str,
    *,
    scale: float = 1.0,
) -> None:
    x, y, width, height = box
    draw.rounded_rectangle((x, y, x + width, y + height), radius=round(28 * scale), fill="#FFFFFF", outline="#CDE1E2", width=max(2, round(3 * scale)))
    circle = round(62 * scale)
    draw.ellipse((x + round(34 * scale), y + round(34 * scale), x + round(34 * scale) + circle, y + round(34 * scale) + circle), fill=TEAL_DARK)
    number_font = _font(round(28 * scale), bold=True)
    number_box = draw.textbbox((0, 0), number, font=number_font)
    number_width = number_box[2] - number_box[0]
    number_height = number_box[3] - number_box[1]
    draw.text((x + round(34 * scale) + (circle - number_width) / 2, y + round(34 * scale) + (circle - number_height) / 2 - number_box[1]), number, font=number_font, fill=WHITE)
    title_x = x + round(124 * scale)
    draw.text((title_x, y + round(32 * scale)), title, font=_font(round(31 * scale), bold=True), fill=INK)
    _draw_wrapped(draw, (title_x, y + round(80 * scale)), body, _font(round(23 * scale)), MUTED, width - round(158 * scale), spacing=round(7 * scale))


def build_print_flyer(logo: Image.Image, hero: Image.Image) -> Image.Image:
    width, height = 2480, 3508
    canvas_image = Image.new("RGB", (width, height), NAVY)
    draw = ImageDraw.Draw(canvas_image)

    hero_height = 1940
    hero_panel = _cover(hero, width, hero_height, focus_x=0.72, focus_y=0.46).convert("RGBA")
    hero_panel.alpha_composite(_gradient_overlay((width, hero_height), 252, 10, horizontal=True))
    hero_panel.alpha_composite(_gradient_overlay((width, hero_height), 0, 150, horizontal=False))
    canvas_image.paste(hero_panel.convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(canvas_image)

    _paste_logo(canvas_image, logo, (140, 105, 720, 255), radius=30)
    draw.rounded_rectangle((140, 410, 790, 487), radius=38, fill=TEAL_DARK)
    draw.text((178, 427), "AI RX LIVE DEMO STUDIO", font=_font(30, bold=True), fill=WHITE)

    draw.text((140, 570), "ADVANCED AI", font=_font(118, bold=True), fill=WHITE)
    draw.text((140, 700), "FOR DOCTORS", font=_font(118, bold=True), fill=TEAL)
    draw.rounded_rectangle((140, 862, 945, 964), radius=50, fill=AMBER)
    draw.text((192, 887), "6-WEEK HANDS-ON PROGRAMME", font=_font(34, bold=True), fill=NAVY)

    intro = (
        "A practical programme for doctors and healthcare professionals to use AI responsibly in clinical reasoning, "
        "patient communication, documentation, research and workflow design."
    )
    _draw_wrapped(draw, (140, 1035), intro, _font(38), WHITE, 1090, spacing=16)
    draw.line((140, 1338, 890, 1338), fill=TEAL, width=7)
    _draw_wrapped(
        draw,
        (140, 1390),
        "Learn the workflow. Question the output. Keep the decision human.",
        _font(38, bold=True),
        CREAM,
        900,
        spacing=14,
    )
    draw.text((140, 1760), "PATIENT FIRST  |  DOCTOR LED  |  AI ASSISTED", font=_font(28, bold=True), fill="#9FE7E1")

    draw.rectangle((0, hero_height, width, height), fill=CREAM)
    draw.text((140, 2035), "WHAT YOU WILL PRACTISE", font=_font(47, bold=True), fill=TEAL_DARK)
    draw.text((140, 2105), "Structured activities built from the current AI Rx workshop resources.", font=_font(27), fill=MUTED)

    card_width = 1050
    card_height = 260
    gap_x = 100
    _feature_card(canvas_image, draw, (140, 2190, card_width, card_height), "01", "Specialty-ready prompts", "Detailed prompts with fictional PDF attachments for practical lab use.")
    _feature_card(canvas_image, draw, (140 + card_width + gap_x, 2190, card_width, card_height), "02", "AI vs Doctor cases", "Compare pattern matching with clinical judgement, context and tacit cues.")
    _feature_card(canvas_image, draw, (140, 2480, card_width, card_height), "03", "Research and documentation", "Source checks, evidence briefs, clinical documentation and workflow labs.")
    _feature_card(canvas_image, draw, (140 + card_width + gap_x, 2480, card_width, card_height), "04", "Responsible decision support", "Privacy, uncertainty, verification, patient communication and human oversight.")

    draw.text((140, 2825), "WHO CAN JOIN?", font=_font(37, bold=True), fill=INK)
    audience = "Doctors  |  Residents  |  Researchers  |  Medical educators  |  Hospital leaders  |  Healthcare and life sciences"
    _draw_wrapped(draw, (140, 2888), audience, _font(27, bold=True), TEAL_DARK, 2180, spacing=10)

    draw.rounded_rectangle((140, 3010, 2340, 3255), radius=34, fill=NAVY_2)
    draw.text((190, 3054), "PROGRAMME ENQUIRIES", font=_font(27, bold=True), fill=AMBER)
    draw.text((190, 3110), "www.publicationpathway.com  |  publicationpathway@gmail.com", font=_font(29, bold=True), fill=WHITE)
    draw.text((190, 3170), "Dr. Shweta Loonkar: +91 99309 22901  |  Dr. Karishma Desai: +91 97696 30494", font=_font(23), fill="#C5DBE1")

    disclaimer = (
        "Educational programme. AI outputs require independent verification by qualified healthcare professionals. "
        "Do not upload identifiable patient information."
    )
    _draw_wrapped(draw, (140, 3310), disclaimer, _font(22), MUTED, 2180, spacing=8)
    draw.rectangle((0, 3483, width, height), fill=TEAL_DARK)
    return canvas_image


def build_social_flyer(logo: Image.Image, hero: Image.Image) -> Image.Image:
    width, height = 1080, 1350
    canvas_image = _cover(hero, width, height, focus_x=0.68, focus_y=0.45).convert("RGBA")
    canvas_image.alpha_composite(_gradient_overlay((width, height), 252, 35, horizontal=True))
    canvas_image.alpha_composite(_gradient_overlay((width, height), 10, 195, horizontal=False))
    canvas_image = canvas_image.convert("RGB")
    draw = ImageDraw.Draw(canvas_image)

    _paste_logo(canvas_image, logo, (58, 50, 390, 132), radius=18)
    draw.rounded_rectangle((58, 215, 425, 262), radius=24, fill=TEAL_DARK)
    draw.text((78, 226), "AI RX LIVE DEMO STUDIO", font=_font(18, bold=True), fill=WHITE)
    draw.text((58, 315), "ADVANCED AI", font=_font(64, bold=True), fill=WHITE)
    draw.text((58, 383), "FOR DOCTORS", font=_font(64, bold=True), fill=TEAL)
    draw.rounded_rectangle((58, 480, 500, 541), radius=30, fill=AMBER)
    draw.text((82, 495), "6-WEEK HANDS-ON PROGRAMME", font=_font(21, bold=True), fill=NAVY)

    _draw_wrapped(
        draw,
        (58, 585),
        "Practical AI workflows for clinical reasoning, patient communication, documentation and research.",
        _font(27),
        WHITE,
        570,
        spacing=10,
    )

    draw.rounded_rectangle((42, 855, 1038, 1205), radius=30, fill=(6, 25, 35, 235))
    draw.text((78, 890), "HANDS-ON LEARNING", font=_font(25, bold=True), fill=AMBER)
    items = [
        "Specialty-ready prompts and fictional PDF cases",
        "AI vs Doctor reasoning and live demonstrations",
        "Research, documentation and workflow labs",
        "Privacy, source checks and human oversight",
    ]
    y = 948
    for item in items:
        draw.ellipse((78, y + 7, 92, y + 21), fill=TEAL)
        y = _draw_wrapped(draw, (110, y), item, _font(22, bold=True), WHITE, 835, spacing=6) + 12

    draw.text((58, 1240), "www.publicationpathway.com", font=_font(24, bold=True), fill=WHITE)
    draw.text((58, 1280), "Educational programme | Qualified professional verification is mandatory", font=_font(17), fill="#C5DBE1")
    return canvas_image


def _write_pdf(image: Image.Image) -> None:
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=96, dpi=(300, 300), optimize=True)
    buffer.seek(0)
    pdf = canvas.Canvas(str(PRINT_PDF), pagesize=A4, pageCompression=1)
    pdf.setTitle("AI Rx Advanced AI for Doctors Flyer")
    pdf.setAuthor("KS Publication Pathway and AI Rx Live Demo Studio")
    pdf.setSubject("Six-week hands-on responsible AI programme for doctors")
    page_width, page_height = A4
    from reportlab.lib.utils import ImageReader

    pdf.drawImage(ImageReader(buffer), 0, 0, width=page_width, height=page_height, preserveAspectRatio=True, mask="auto")
    pdf.showPage()
    pdf.save()


def main() -> None:
    if not SOURCE_LOGO.exists():
        raise FileNotFoundError(SOURCE_LOGO)
    if not HERO.exists():
        raise FileNotFoundError(HERO)
    MARKETING.mkdir(parents=True, exist_ok=True)
    logo = _crop_logo()
    hero = Image.open(HERO).convert("RGB")
    print_flyer = build_print_flyer(logo, hero)
    social_flyer = build_social_flyer(logo, hero)
    print_flyer.save(PRINT_PNG, format="PNG", dpi=(300, 300), optimize=True)
    social_flyer.save(SOCIAL_PNG, format="PNG", dpi=(144, 144), optimize=True)
    _write_pdf(print_flyer)
    print(f"Created {CROPPED_LOGO.relative_to(ROOT)}")
    print(f"Created {PRINT_PNG.relative_to(ROOT)}")
    print(f"Created {PRINT_PDF.relative_to(ROOT)}")
    print(f"Created {SOCIAL_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
