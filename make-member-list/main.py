from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROW_LEN = 8
COLUMN_LEN = 8
AVATAR_SIZE = 64
FONT_SIZE = 20
RIGHT_PADDING = 180
BOTTOM_PADDING = 20

images = list(Path("avatars").glob("*.png"))
background = Image.new(
    "RGBA",
    (
        ROW_LEN * (AVATAR_SIZE + RIGHT_PADDING),
        COLUMN_LEN * (AVATAR_SIZE + BOTTOM_PADDING) - BOTTOM_PADDING,
    ),
    0,
)


for row in range(ROW_LEN):
    row_width = row * (AVATAR_SIZE + RIGHT_PADDING)
    for column in range(COLUMN_LEN):
        column_height = column * (AVATAR_SIZE + BOTTOM_PADDING)
        try:
            file = images.pop()
        except IndexError:
            break

        avatar = Image.open(file).resize((AVATAR_SIZE, AVATAR_SIZE))
        background.paste(avatar, (row_width, column_height))

        imd = ImageDraw.Draw(background)
        imd.text(
            (
                row_width + AVATAR_SIZE + 15,
                column_height + AVATAR_SIZE / 2 - FONT_SIZE / 2,
            ),
            file.stem,
            fill=(255, 255, 255),
            font=ImageFont.truetype("arial.ttf", FONT_SIZE),
        )

        print(f"{row:02}-{column:02}: {file.stem}")

background.save("CT_member.png")
