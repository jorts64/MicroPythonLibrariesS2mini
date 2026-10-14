import tm1638
from machine import Pin
from time import sleep
tm = tm1638.TM1638(stb=Pin(16), clk=Pin(15), dio=Pin(14))

# every 2nd LED on
tm.leds(0b01010101)
sleep(1)
# all LEDs off
tm.leds(0)
sleep(1)
tm.led(0,1)
sleep(1)
# segments
tm.show('cool')
tm.led(1,1)
sleep(2)
tm.scroll("abcdefghijklmnopqrstuvwxyz", delay=250)
tm.led(2,1)
sleep(2)
tm.number(-1234567)
tm.led(3,1)
sleep(2)
tm.number(1234)
tm.led(4,1)
sleep(2)
tm.clear()
tm.temperature(21)
tm.led(5,1)
sleep(2)
tm.humidity(85)
tm.led(6,1)
sleep(2)
tm.hex(0xdeadbeef)
tm.led(7,1)
sleep(2)
tm.leds(0)

# dim both LEDs and segments
tm.brightness(0)
sleep(2)

# all LEDs and segments off
tm.clear()
sleep(2)

# get which buttons are pressed on LED&KEY module
tm.scroll("mantenga pulsado botones", delay=500)
tm.hex(tm.keys(),)
sleep(2)
tm.clear()

# Funcion implementada por Jordi Orts 2026
tm.decimal(12.6, 1, 4)    # 12.6 empezando en la posición 4
sleep(2)
tm.clear()
tm.decimal(3.14159, 2, 0) # 3.14
sleep(2)
tm.clear()
tm.decimal(25, 2, 0)      # 25.00
sleep(2)
tm.clear()
tm.decimal(-7.5, 1, 0)    # -7.5
sleep(2)
tm.clear()



