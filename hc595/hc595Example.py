import hc595
import time


# ============================================================
# CONFIGURACIÓN
# ============================================================

# 3 chips = 24 salidas
NUM_CHIPS = 3

# Pines de la LOLIN S2 Mini
DATA_PIN  = 11     # LDSI
CLOCK_PIN = 12     # LDSCK
LATCH_PIN = 13     # LDSTR
OE_PIN    = 14     # LEDEN / OE


# ============================================================
# INICIALIZACIÓN
# ============================================================

print("Inicializando 74HC595...")

hc595.init(
    NUM_CHIPS,
    DATA_PIN,
    CLOCK_PIN,
    LATCH_PIN,
    OE_PIN
)

print("Chips:", NUM_CHIPS)
print("Salidas:", NUM_CHIPS * 8)


# ============================================================
# 1. EMPTY
# ============================================================

print("1 - EMPTY")

hc595.empty()

print("Registro:", hex(hc595.getall()))

time.sleep(1)


# ============================================================
# 2. SET
# ============================================================

print("2 - SET")

# Encender varias salidas
hc595.set(0)
hc595.set(5)
hc595.set(10)
hc595.set(15)
hc595.set(20)

print("Registro:", hex(hc595.getall()))

time.sleep(1)


# ============================================================
# 3. GET
# ============================================================

print("3 - GET")

for pin in range(24):
    print("Pin", pin, "=", hc595.get(pin))

time.sleep(1)


# ============================================================
# 4. CLEAR
# ============================================================

print("4 - CLEAR")

# Apagar algunas salidas
hc595.clear(5)
hc595.clear(15)

print("Registro:", hex(hc595.getall()))

time.sleep(1)


# ============================================================
# 5. GETALL
# ============================================================

print("5 - GETALL")

registro = hc595.getall()

print("Registro decimal:", registro)
print("Registro hexadecimal:", hex(registro))
print("Registro binario:", bin(registro))

time.sleep(1)


# ============================================================
# 6. SETALL
# ============================================================

print("6 - SETALL")

# Encender las salidas 0, 4, 8, 12, 16 y 20
#
# 000000
# 000001
#
# Bits:
# 20,16,12,8,4,0

valor = (
    (1 << 0)  |
    (1 << 4)  |
    (1 << 8)  |
    (1 << 12) |
    (1 << 16) |
    (1 << 20)
)

hc595.setall(valor)

print("Valor enviado:", hex(valor))
print("Valor leído:", hex(hc595.getall()))

time.sleep(1)


# ============================================================
# 7. DISABLE
# ============================================================

print("7 - DISABLE")

# Deshabilita físicamente las salidas.
#
# El registro NO se modifica.

print("Registro antes:", hex(hc595.getall()))

hc595.disable()

print("Salidas deshabilitadas")

time.sleep(2)


# ============================================================
# 8. ENABLE
# ============================================================

print("8 - ENABLE")

# Vuelve a habilitar las salidas.
#
# Aparecerá de nuevo el contenido
# que estaba almacenado en el registro.

hc595.enable()

print("Salidas habilitadas")
print("Registro:", hex(hc595.getall()))

time.sleep(2)


# ============================================================
# 9. FULL
# ============================================================

print("9 - FULL")

# Enciende las 24 salidas

hc595.full()

print("Registro:", hex(hc595.getall()))

time.sleep(2)


# ============================================================
# 10. EMPTY
# ============================================================

print("10 - EMPTY")

# Apaga las 24 salidas

hc595.empty()

print("Registro:", hex(hc595.getall()))

time.sleep(2)


# ============================================================
# 11. TEST
# ============================================================

print("11 - TEST")

# Enciende las 24 salidas una a una.
#
# 0 -> 1 -> 2 -> ... -> 23

hc595.test(0.2)

print("Test terminado")


# ============================================================
# FIN
# ============================================================

print("Ejemplo terminado")

hc595.empty()