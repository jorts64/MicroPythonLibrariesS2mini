from machine import Pin, I2C
from time import sleep, sleep_ms
from ssd1306_fonts import SSD1306_I2C
from sht30 import SHT30
i2c = I2C(0,scl=Pin(35),sda=Pin(33),freq=400000)
print("I2C:", [hex(x) for x in i2c.scan()])
sht30 = SHT30(i2c, 0x44)
oled = SSD1306_I2C(128, 64, i2c, 0x3C)

x=0
oled.fill(0)

def pinta_temp():
    global x
    tmax=45
    temperatura = int(sht30.temperature)
    if x <= oled.width-1:
        oled.pixel(x,tmax-temperatura,1)
        x = x+1
    else:
        oled.scroll(-1,0)
        oled.vline(oled.width-1,0,oled.height,0)
        oled.pixel(oled.width-1,tmax-temperatura,1)
    oled.show()

while True:
    sht30.measure()
    print("Temperatura: {:.2f} C".format(sht30.temperature))
    print("Humedad: {:.2f} %".format(sht30.humidity))
    pinta_temp()
    sleep_ms(300)

