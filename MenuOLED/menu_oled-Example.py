
from machine import Pin, I2C

from sh1116_fonts import SH1116_I2C
import vga2_fonts_8x16 as font2
from encoder import EncoderKnob

from menu_oled import MenuOLED


# --------------------------------------------------
# 1. Inicializar I2C y pantalla SH1116
# --------------------------------------------------

i2c = I2C(
    0,
    scl=Pin(36),
    sda=Pin(34),
    freq=400000
)

oled = SH1116_I2C(
    128,
    64,
    i2c,
    addr=0x3C,
    external_vcc=False,
    col_offset=2
)


# --------------------------------------------------
# 2. Funciones de las opciones del menu
# --------------------------------------------------

def mostrar_info():
    print("Informacion del sistema")


def ajustar_brillo():
    print("Ajustar brillo")


def leer_sensor():
    print("Leer sensor")


def mostrar_mensaje():
    print("Hola desde el menu")


temperatura_objetivo = 25

def guardar_temperatura(valor):
    global temperatura_objetivo

    temperatura_objetivo = valor
    print("Temperatura:", temperatura_objetivo)


from machine import ADC, Pin
import time

# adc_pins = [1, 2, 3]
adc_pins = list(range(1, 17))
adc_index = 0
adc_activo = False


def ADC_leer():
    global adc_activo, adc_index

    adc_activo = True
    adc_index = 0

    menu.disable(ADC_sel, ADC_end)

    oled.fill(0)
    oled.show()


def ADC_sel(delta):
    global adc_index

    if not adc_activo:
        return

    adc_index = (adc_index + (1 if delta > 0 else -1)) % len(adc_pins)


def ADC_end():
    global adc_activo

    adc_activo = False
    menu.restore()

def ADC_actualizar():
    if not adc_activo:
        return

    pin = adc_pins[adc_index]
    adc = ADC(Pin(pin))
    valor = adc.read()

    oled.fill(0)
    oled.draw_text("Lectura ADC", 0, 0, font2)
    oled.draw_text("GPIO: {}".format(pin), 0, 16, font2)
    oled.draw_text("Valor: {}".format(valor), 0, 32, font2)
    oled.draw_text("Pulsar: salir", 0, 48, font2)
    oled.show()

# --------------------------------------------------
# 3. Preparar callbacks del encoder
# --------------------------------------------------

# El encoder necesita recibir los callbacks al crearse.
# Esta referencia permite conectarlos al menu despues.

menu_ref = [None]


def rotated(delta):
    if menu_ref[0] is not None:
        menu_ref[0].rotated(delta)


def pressed():
    if menu_ref[0] is not None:
        menu_ref[0].pressed()


enc = EncoderKnob(
    38,
    39,
    btn_pin=37,
    rotary_callback=rotated,
    btn_callback=pressed
)


# --------------------------------------------------
# 4. Crear el sistema de menus
# --------------------------------------------------

menu = MenuOLED(oled, enc, font2)


# Menu raiz: menu 0

menu.add(0, 0, "Configuracion", submenu=1)
menu.add(0, 1, "Informacion", mostrar_info)
menu.add(0, 2, "Sensores", submenu=2)
menu.add(0, 3, "Mensaje", mostrar_mensaje)
menu.add(0, 4, "Leer ADCs", ADC_leer) 

# Menu 1: configuracion

menu.add(1, 0, "< Volver")
menu.add(1, 1, "Brillo", ajustar_brillo)


# Menu 2: sensores

menu.add(2, 0, "< Volver")
menu.add(2, 1, "Leer sensor", leer_sensor)


menu.add_number(
    0,                    # Menu
    5,                    # Posicion
    "Temperatura",        # Texto
    temperatura_objetivo, # Valor inicial
    10,                   # Minimo
    35,                   # Maximo
    step=1,               # Incremento
    callback=guardar_temperatura
)


# --------------------------------------------------
# 5. Arrancar el sistema
# --------------------------------------------------

menu_ref[0] = menu

menu.start()


# Desde cualquier funcion puedes usar:
#
# menu.selmenu(0)  -> ir al menu raiz
# menu.selmenu(1)  -> abrir el menu 1
# menu.selmenu(2)  -> abrir el menu 2

while True:
    if adc_activo:
        ADC_actualizar()

    time.sleep_ms(200)