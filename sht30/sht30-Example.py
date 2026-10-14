from machine import Pin, I2C
from time import sleep, sleep_ms
from ssd1306_fonts import SSD1306_I2C
import vga2_fonts_8x8 as font
import vga2_fonts_8x16 as font2
from sht30 import SHT30

i2c = I2C(
    0,
    scl=Pin(35),
    sda=Pin(33),
    freq=400000
)

print("I2C:", [hex(x) for x in i2c.scan()])

# Crear el objeto SHT30
sht30 = SHT30(i2c, 0x44)

while True:
    sht30.measure()

    print("Temperatura: {:.2f} C".format(sht30.temperature))
    print("Humedad: {:.2f} %".format(sht30.humidity))

    sleep(2)
