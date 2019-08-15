from PIL import Image, ImageDraw, ImageFont


class Watermark(object):
    def process(self, img):
        #font = ImageFont.load_default().font
        font = ImageFont.truetype("fonts/arialbd.ttf",40)
        #fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf',15)
        draw = ImageDraw.Draw(img)
        draw.text((40,40), "GASOFORUM",font=font, fill=('#f0f0f0'))
        #draw.line((0, 0) + img.size, fill=128)
        #draw.line((0, img.size[1], img.size[0], 0), fill=128)
        return img