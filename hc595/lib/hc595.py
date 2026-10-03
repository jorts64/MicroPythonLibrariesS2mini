from machine import Pin
import time


_num_chips = 0
_num_outputs = 0

_data = None
_clock = None
_latch = None
_oe = None

_register = 0


def init(num_chips, data_pin, clock_pin, latch_pin, oe_pin):
    """
    Inicializa los 74HC595.

    num_chips : número de chips conectados en cascada
    data_pin  : GPIO para LDSI
    clock_pin : GPIO para LDSCK
    latch_pin : GPIO para LDSTR
    oe_pin    : GPIO para LEDEN / OE
    """

    global _num_chips
    global _num_outputs
    global _data, _clock, _latch, _oe
    global _register

    _num_chips = num_chips
    _num_outputs = num_chips * 8

    _data = Pin(data_pin, Pin.OUT, value=0)
    _clock = Pin(clock_pin, Pin.OUT, value=0)
    _latch = Pin(latch_pin, Pin.OUT, value=0)

    # OE es activo en LOW.
    # Empezamos con las salidas deshabilitadas.
    _oe = Pin(oe_pin, Pin.OUT, value=1)

    # Registro interno a cero
    _register = 0

    # Enviar ceros a los 74HC595
    _write()

    # Habilitar las salidas
    enable()


def _write():
    """Envía el registro interno a los 74HC595."""

    _latch.value(0)

    for i in range(_num_outputs):
        bit = (_register >> (_num_outputs - 1 - i)) & 1

        _data.value(bit)

        _clock.value(1)
        _clock.value(0)

    # Transferir el registro de desplazamiento
    # al registro de salida.
    _latch.value(1)
    _latch.value(0)


def enable():
    """Habilita las salidas (OE = 0)."""

    _oe.value(0)


def disable():
    """Deshabilita las salidas (OE = 1)."""

    _oe.value(1)


def full():
    """Enciende todas las salidas."""

    global _register

    _register = (1 << _num_outputs) - 1
    _write()


def empty():
    """Apaga todas las salidas."""

    global _register

    _register = 0
    _write()


def set(pin):
    """
    Enciende una salida sin modificar las demás.

    pin = 0 ... (num_chips * 8 - 1)
    """

    global _register

    if pin < 0 or pin >= _num_outputs:
        return False

    _register |= (1 << pin)
    _write()

    return True


def clear(pin):
    """
    Apaga una salida sin modificar las demás.

    pin = 0 ... (num_chips * 8 - 1)
    """

    global _register

    if pin < 0 or pin >= _num_outputs:
        return False

    _register &= ~(1 << pin)
    _write()

    return True


def get(pin):
    """
    Devuelve el estado de una salida.

    True  = encendida
    False = apagada
    """

    if pin < 0 or pin >= _num_outputs:
        return False

    return bool(_register & (1 << pin))


def getall():
    """
    Devuelve el registro completo como entero.
    """

    return _register


def setall(value):
    """
    Carga el registro completo y actualiza las salidas.

    Ejemplos:

        setall(0x00)       -> todo apagado
        setall(0xFF)       -> 8 salidas encendidas
        setall(0xFFFF)     -> 16 salidas encendidas
        setall(0xFFFFFF)   -> 24 salidas encendidas
    """

    global _register

    max_value = (1 << _num_outputs) - 1

    # Comprobar que el valor es válido
    if value < 0 or value > max_value:
        return False

    _register = value
    _write()

    return True


def test(delay=0.1):
    """
    Enciende las salidas una a una.
    """

    global _register

    empty()

    for pin in range(_num_outputs):
        _register = 1 << pin
        _write()
        time.sleep(delay)

    empty()