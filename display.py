from PIL import Image
from data import grab_game, derive_state
from fonts import FONT_LARGE, FONT_SMALL
import time
# ==================================================
# DRAW HELPERS
# ==================================================
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    HAS_MATRIX = True
except ImportError:
    HAS_MATRIX = False
SIMULATE = False


def safe(val, default=""):
    return default if val is None else str(val)

def init_matrix():
    if not HAS_MATRIX:
        raise RuntimeError("rgbmatrix not available")

    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1

    # tune these 
    options.brightness = 40
    options.hardware_mapping = 'adafruit-hat'
    options.gpio_slowdown = 2

    return RGBMatrix(options=options)

def draw_text(img, text, x, y, font, char_w, char_h, spacing, color=(255, 255, 255)):
    px = img.load()

    for ch in text:
        glyph = font.get(ch.upper(), font[" "])

        # Safety check (optional but recommended while debugging)
      #   if len(glyph) != char_w * char_h:
      #       for ch in away:
      #             print(ch, len(FONT_LARGE[ch]))
      #       raise ValueError(f"Glyph '{ch}' has wrong length: {len(glyph)}")

        for r in range(char_h):
            for c in range(char_w):
                idx = r * char_w + c  # <-- THIS IS THE KEY FIX
                if glyph[idx] == "#":
                    xx = x + c
                    yy = y + r
                    if 0 <= xx < img.width and 0 <= yy < img.height:
                        px[xx, yy] = color

        x += char_w + spacing
def text_width(text, char_w, spacing):
    return len(text) * (char_w + spacing)

def draw_pregame(img, data):
    draw_text(img, data["awayName"], 2, 10, FONT_LARGE, 5, 7, 1)
    draw_text(img, "AT", 25, 11, FONT_SMALL, 3, 5, 1)
    draw_text(img, data["homeName"], 38, 10, FONT_LARGE, 5, 7, 1)

    #draw_text(img, data["startTime"], 20, 22, FONT_SMALL, 3, 5, 1)
    draw_text(img, safe(data.get("startTime")), 20, 22, FONT_SMALL, 3, 5, 1)


def draw_live(img, data):
    draw_text(img, data["awayName"], 2, 4, FONT_LARGE, 5, 7, 1)
    draw_text(img, str(data["awayScore"]), 22, 4, FONT_LARGE, 5, 7, 1)

    draw_text(img, data["homeName"], 2, 18, FONT_LARGE, 5, 7, 1)
    draw_text(img, str(data["homeScore"]), 22, 18, FONT_LARGE, 5, 7, 1)

    # draw_text(img, data["gameClock"], 44, 6, FONT_SMALL, 3, 5, 1)
    # draw_text(img, f"{data['period']}Q", 46, 20, FONT_SMALL, 3, 5, 1)

    draw_text(img, safe(data.get("gameClock")), 44, 6, FONT_SMALL, 3, 5, 1)
    draw_text(img, f"{safe(data.get('period'))}Q", 46, 20, FONT_SMALL, 3, 5, 1)

def draw_halftime(img, data):
    draw_text(img, data["awayName"], 2, 4, FONT_LARGE, 5, 7, 1)
    draw_text(img, str(data["awayScore"]), 22, 4, FONT_LARGE, 5, 7, 1)

    draw_text(img, data["homeName"], 2, 18, FONT_LARGE, 5, 7, 1)
    draw_text(img, str(data["homeScore"]), 22, 18, FONT_LARGE, 5, 7, 1)

    draw_text(img, "HT", 40, 20, FONT_SMALL, 3, 5, 1)

def draw_final(img, data):
    draw_text(img, data["awayName"], 2, 4, FONT_LARGE, 5, 7, 1)
    draw_text(img, str(data["awayScore"]), 22, 4, FONT_LARGE, 5, 7, 1)

    draw_text(img, data["homeName"], 2, 18, FONT_LARGE, 5, 7, 1)
    draw_text(img, str(data["homeScore"]), 22, 18, FONT_LARGE, 5, 7, 1)

    draw_text(img, "F", 46, 20, FONT_SMALL, 3, 5, 1)
    
# ==================================================
# MAIN (64x32 MOCK DISPLAY)
# ==================================================

def render_frame(data, state):
    img = Image.new("RGB", (WIDTH, HEIGHT), "black")

    if not data:
        draw_text(img, "NO DATA", 10, 12, FONT_LARGE, 5, 7, 1)
        return img

    if state == "SCHEDULED":
        draw_pregame(img, data)
    elif state == "HALFTIME":
        draw_halftime(img, data)
    elif state == "LIVE":
        draw_live(img, data)
    elif state == "FINAL":
        draw_final(img, data)

    return img


matrix = None  # global, initialized lazily

def output_frame(img):
    global matrix

    if SIMULATE:
        img.resize((WIDTH * 8, HEIGHT * 8), Image.NEAREST).show()
        return

    if not HAS_MATRIX:
        raise RuntimeError("SIMULATE=False but rgbmatrix not available")

    if matrix is None:
        matrix = init_matrix()

    matrix.SetImage(img)




REFRESH_SECONDS = 10
WIDTH, HEIGHT = 64, 32
def main():
    while True:
        try:
            data = grab_game()
            state = derive_state(data)

            print(f"{time.strftime('%H:%M:%S')} | {state} | {data['statusText']} |")

            img = render_frame(data, state)
            output_frame(img)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    main()
