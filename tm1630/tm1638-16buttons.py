import tm1638
from machine import Pin
from time import sleep
tm = tm1638.TM1638(stb=Pin(16), clk=Pin(15), dio=Pin(14), display_layout="matrix")


# segments
tm.show('cool')
sleep(2)
tm.scroll("abcdefghijklmnopqrstuvwxyz", delay=250)
sleep(2)
tm.number(-1234567)
sleep(2)
tm.number(1234)
sleep(2)
tm.clear()
tm.temperature(21)
sleep(2)
tm.humidity(85)
sleep(2)
tm.hex(0xdeadbeef)
sleep(2)

# dim both LEDs and segments
tm.brightness(0)
sleep(2)

# all LEDs and segments off
tm.clear()
sleep(2)


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


# get which buttons are pressed
tm.scroll("mantenga pulsado botones", delay=500)
while True:
    print(tm.keys(),)
    tm.clear()
    tm.hex(tm.keys(),)
    sleep(2)

