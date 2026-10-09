from machine import Pin, I2C
from time import sleep, sleep_ms
from ssd1306_fonts import SSD1306_I2C
import vga2_fonts_8x8 as font
import vga2_fonts_8x16 as font2

i2c = I2C(
    0,
    scl=Pin(35),
    sda=Pin(33),
    freq=400000
)

oled = SSD1306_I2C(
    128,
    64,
    i2c,
    0x3C
)

oled.draw_text("vúmetro", 0, 16, font)
for l in range(101):
    font2.vumeter(oled, -1,   4, 100, 0)
    font2.vumeter(oled, l,   4, 100, 0)
    oled.show()
    sleep_ms(10)
sleep(2)


oled.fill(0)
oled.draw_text("Indicador", 0, 0, font)
oled.draw_text("Batería", 0, 8, font)
for l in range(101):
    font2.battery(oled, -1, 112, 0)
    font2.battery(oled, l, 112, 0)
    oled.show()
    sleep_ms(20)

# oled.fill(0)
oled.draw_text("Indicador", 0, 16, font)
oled.draw_text("Progreso", 0, 24, font)
for l in range(101):
    font2.bar_done(oled, -1, 5, 80, 16)
    font2.bar_done(oled, l, 5, 80, 16)
    oled.show()
    sleep_ms(10)
sleep(2)


oled.fill(0)
oled.draw_text("AÁÀÄEÉÈËIÍÌÏOÓÒÖ", 0, 0, font)
oled.draw_text("UÚÙÜNÑCÇ", 0, 8, font)
oled.draw_text("aáàäeéèëiíìïoóòö", 0, 16, font)
oled.draw_text("uúùünñcç", 0, 24, font)
oled.show()
sleep(2)

oled.fill(0)
oled.draw_text("AÁÀÄEÉÈËIÍÌÏOÓÒÖ", 0, 0, font2)
oled.draw_text("UÚÙÜNÑCÇ", 0, 16, font2)
oled.draw_text("aáàäeéèëiíìïoóòö", 0, 32, font2)
oled.draw_text("uúùünñcç", 0, 48, font2)
oled.show()
sleep(2)

oled.fill(0)

oled.charset(font,2)
sleep(2)
oled.charset(font2,2)

sleep(2)
oled.fill(0)

oled.line(0, 0, 127, 63)
oled.show()
sleep(1)
oled.hline(0, 32, 128)
oled.show()
sleep(1)
oled.vline(64, 0, 64)
oled.show()
sleep(1)

oled.rect(10, 10, 50, 20)
oled.show()
sleep(1)
oled.fill_rect(70, 10, 40, 20)
oled.show()
sleep(1)

oled.ellipse(32, 48, 20, 10)
oled.show()
sleep(1)
oled.ellipse(96, 48, 20, 10, 1, True)
oled.show()
sleep(1)

oled.poly(
    32, 48,
    (0, -7, 7, 7, -7, 7),
    1,
    True
)
oled.show()


for i in range(128):
    oled.scroll(-1, 0)
    oled.show()
    sleep_ms(5)

sleep(1)

import framebuf

buf = bytearray(16 * 16)
sprite = framebuf.FrameBuffer1(buf, 16, 16)

for x in range(0, 128 - 16, 2):

#     oled.fill(0)

    sprite.fill(0)
    sprite.fill_rect(2, 2, 12, 12, 1)
    sprite.fill_rect(5, 5, 6, 6, 0)

    oled.blit(sprite, x, 24)

    oled.show()
    sleep_ms(5)

