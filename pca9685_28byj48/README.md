# PCA9685 + 28BYJ-48 para MicroPython

Biblioteca para controlar hasta **4 motores paso a paso 28BYJ-48 con ULN2003 por cada PCA9685**, usando un LOLIN S2 Mini y MicroPython.

El PCA9685 genera de forma autónoma las cuatro señales necesarias para cada motor mediante PWM desfasado. El S2 Mini solo configura el PCA9685 por I²C; no tiene que generar los pasos del motor.

## Características

- Hasta 4 motores 28BYJ-48 por PCA9685.
- Cada motor utiliza 4 canales consecutivos.
- Hasta 16 canales por PCA9685.
- Varios PCA9685 en el mismo bus I²C.
- Velocidad independiente por PCA9685.
- Los cuatro motores de una misma placa comparten la velocidad de esa placa.
- Sentido independiente por motor: `cw()` y `ccw()`.
- `stop()` desenergiza las bobinas.
- `lock()` mantiene una fase activada para bloquear el rotor.
- Control opcional de `OE`.
- `oe_pin=-1` significa que OE no está conectado.
- No requiere una librería externa para el PCA9685.

## Arquitectura

```text
                         LOLIN S2 Mini
                              │
                              │ I²C
                ┌─────────────┼─────────────┐
                │             │             │
             PCA9685       PCA9685       PCA9685
              0x40          0x41          0x42
                │             │             │
          ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐
          │           │ │           │ │           │
       ULN2003      ULN2003      ULN2003        ...
          │           │
       28BYJ-48    28BYJ-48
```

Cada PCA9685 dispone de 16 canales:

```text
Motor 0 → CH0  CH1  CH2  CH3
Motor 1 → CH4  CH5  CH6  CH7
Motor 2 → CH8  CH9  CH10 CH11
Motor 3 → CH12 CH13 CH14 CH15
```

## Hardware

Por cada motor se necesita un 28BYJ-48 y su placa ULN2003. Además, un LOLIN S2 Mini, uno o varios PCA9685 y una fuente adecuada para los motores.

### LOLIN S2 Mini → PCA9685

Ejemplo usando GPIO 33 y 35:

| LOLIN S2 Mini | PCA9685 |
|---|---|
| GPIO 33 | SDA |
| GPIO 35 | SCL |
| GND | GND |
| 3.3 V | VCC |

En MicroPython:

```python
from machine import Pin, I2C

i2c = I2C(
    0,
    scl=Pin(35),
    sda=Pin(33),
    freq=400_000
)
```

Los GPIO de SDA y SCL pueden cambiarse si se desea.

### Alimentación

El ULN2003 debe recibir la alimentación correspondiente al 28BYJ-48, normalmente 5 V para las versiones habituales. No se debe alimentar un conjunto de varios motores desde el LOLIN S2 Mini.

Es necesario compartir masa entre LOLIN, PCA9685 y ULN2003:

```text
LOLIN GND
     │
     ├── PCA9685 GND
     │
     └── ULN2003 GND
```

La fuente debe dimensionarse para la corriente total de los motores que puedan funcionar simultáneamente.

## OE

El PCA9685 dispone de `OE` (Output Enable). La biblioteca permite conectarlo a un GPIO del S2 Mini:

```python
board = PCA9685Board(i2c, address=0x40, oe_pin=5)
```

La lógica es:

```text
OE = 0 → salidas habilitadas
OE = 1 → salidas deshabilitadas
```

Por tanto:

```python
board.oe_on()
board.oe_off()
```

Si OE no está conectado:

```python
board = PCA9685Board(i2c, address=0x40, oe_pin=-1)
```

En ese caso `oe_on()` y `oe_off()` no realizan ninguna acción.

## Direcciones I²C

Cada PCA9685 debe tener una dirección diferente. Por ejemplo:

```text
PCA9685 #1 → 0x40
PCA9685 #2 → 0x41
PCA9685 #3 → 0x42
```

Para comprobar las direcciones:

```python
print([hex(x) for x in i2c.scan()])
```

## Instalación

La biblioteca consiste en un único archivo:

```text
pca9685_28byj48.py
```

Debe copiarse a la memoria del LOLIN S2 Mini, preferiblemente a la carpeta lib:

```text
/
├── boot.py
├── main.py
└── lib
      └── pca9685_28byj48.py
```

No se necesita instalar otra librería para el PCA9685.

## Importación

```python
from pca9685_28byj48 import PCA9685Board
```

# API: `PCA9685Board`

Representa un PCA9685 completo.

## Constructor

```python
PCA9685Board(i2c, address=0x40, oe_pin=-1)
```

- `i2c`: objeto `machine.I2C`.
- `address`: dirección I²C del PCA9685, por defecto `0x40`.
- `oe_pin`: GPIO para OE; `-1` significa que no está conectado.

## `set_speed(rpm)`

Establece la velocidad de los cuatro motores de esa placa:

```python
board.set_speed(10)
```

Cada PCA9685 puede tener una velocidad diferente, pero los cuatro motores conectados a una misma placa comparten esa velocidad.

## `motor(number)`

Devuelve el motor `0..3`:

```python
motor = board.motor(0)
```

Los canales son:

| Motor | Canales |
|---|---|
| 0 | CH0–CH3 |
| 1 | CH4–CH7 |
| 2 | CH8–CH11 |
| 3 | CH12–CH15 |

Cada grupo se conecta a `IN1..IN4` de su ULN2003.

## `stop_all()`

Para y desenergiza todos los motores de la placa:

```python
board.stop_all()
```

## `lock_all()`

Bloquea todos los motores manteniendo una fase activada:

```python
board.lock_all()
```

## `oe_on()` / `oe_off()`

Habilitan o deshabilitan las salidas si OE está conectado:

```python
board.oe_on()
board.oe_off()
```

## `oe_connected()`

Devuelve `True` si se configuró un pin OE:

```python
if board.oe_connected():
    print("OE conectado")
```

# API: `Stepper28BYJ48`

Se obtiene mediante:

```python
motor = board.motor(0)
```

## `cw()`

Giro horario:

```python
motor.cw()
```

El PCA9685 genera continuamente las señales; MicroPython no ejecuta los pasos.

## `ccw()`

Giro antihorario:

```python
motor.ccw()
```

## `stop()`

Desactiva las cuatro salidas del motor:

```python
motor.stop()
```

El motor queda sin corriente y sin par de mantenimiento.

## `lock()`

Para el motor manteniendo una fase activada:

```python
motor.lock()
```

El estado es:

```text
1000
```

Es decir, una fase activada y las otras tres apagadas. El motor mantiene par y continúa consumiendo corriente.

## Velocidad y secuencia

La biblioteca utiliza half-step:

```text
Paso   A B C D

  0    1 0 0 0
  1    1 1 0 0
  2    0 1 0 0
  3    0 1 1 0
  4    0 0 1 0
  5    0 0 1 1
  6    0 0 0 1
  7    1 0 0 1
```

Se utiliza el valor nominal de `4096 pasos/vuelta` y 8 pasos por ciclo PWM. La frecuencia se calcula como:

```text
PWM = RPM × 4096 / (60 × 8)
```

Por ejemplo, 10 RPM requieren aproximadamente 85,33 Hz. El prescaler entero del PCA9685 hace que la frecuencia real pueda diferir ligeramente.

El S2 Mini configura los registros y el PCA9685 genera las señales de forma autónoma.

# Ejemplos

## Un PCA9685

```python
from machine import Pin, I2C
from pca9685_28byj48 import PCA9685Board

i2c = I2C(
    0,
    scl=Pin(35),
    sda=Pin(33),
    freq=400_000
)

board = PCA9685Board(
    i2c,
    address=0x40,
    oe_pin=5
)

board.set_speed(10)

motor0 = board.motor(0)
motor1 = board.motor(1)
motor2 = board.motor(2)
motor3 = board.motor(3)

motor0.cw()
motor1.ccw()
motor2.cw()
motor3.ccw()
```

## Dos PCA9685 con velocidades diferentes

```python
from machine import Pin, I2C
from pca9685_28byj48 import PCA9685Board

i2c = I2C(
    0,
    scl=Pin(35),
    sda=Pin(33),
    freq=400_000
)

board1 = PCA9685Board(i2c, address=0x40, oe_pin=5)
board2 = PCA9685Board(i2c, address=0x41, oe_pin=6)

board1.set_speed(10)
board2.set_speed(5)

motor1 = board1.motor(0)
motor2 = board1.motor(1)
motor3 = board2.motor(0)
motor4 = board2.motor(1)

motor1.cw()
motor2.ccw()
motor3.cw()
motor4.ccw()
```

Resultado:

```text
PCA9685 0x40
    motor 0 → horario      → 10 RPM
    motor 1 → antihorario  → 10 RPM

PCA9685 0x41
    motor 0 → horario      → 5 RPM
    motor 1 → antihorario  → 5 RPM
```

## Cuatro motores por placa

```python
board1.set_speed(10)

board1.motor(0).cw()
board1.motor(1).ccw()
board1.motor(2).cw()
board1.motor(3).ccw()
```

## OE

```python
board = PCA9685Board(i2c, 0x40, oe_pin=5)
board.set_speed(10)
board.motor(0).cw()

board.oe_off()   # deshabilita las salidas
board.oe_on()    # vuelve a habilitarlas
```

## Cambiar velocidad mientras funciona

```python
board.set_speed(5)
board.set_speed(10)
```

No es necesario volver a llamar a `cw()` o `ccw()`.

## Cambiar de sentido

```python
motor.cw()
motor.ccw()
```

# Limitaciones y notas

### Velocidad por placa

Los cuatro motores de un PCA9685 comparten la frecuencia PWM. Por tanto, esto es posible:

```text
PCA9685 #1 → 10 RPM
PCA9685 #2 → 5 RPM
```

pero no esto:

```text
PCA9685 #1
motor 0 → 5 RPM
motor 1 → 10 RPM
motor 2 → 15 RPM
motor 3 → 20 RPM
```

### 4096 pasos/vuelta

`4096` es el valor nominal habitual para el 28BYJ-48 en half-step. Las unidades comerciales pueden variar ligeramente por la relación real de engranajes. Para posicionamiento de precisión conviene calibrar el motor concreto.

### Velocidad máxima

La velocidad práctica depende de alimentación, carga, motor, engranajes, inercia y aceleración. Una frecuencia PWM elevada del PCA9685 no garantiza que el 28BYJ-48 pueda seguir los pasos.

### Alimentación

Con varios motores simultáneos debe utilizarse una fuente de 5 V adecuada. No se debe hacer pasar la corriente de los motores por el LOLIN S2 Mini. `lock()` mantiene una fase energizada, por lo que el motor continúa consumiendo corriente.

# API resumida

## `PCA9685Board`

```python
PCA9685Board(i2c, address=0x40, oe_pin=-1)
```

```python
board.set_speed(rpm)
board.motor(number)
board.stop_all()
board.lock_all()
board.oe_on()
board.oe_off()
board.oe_connected()
```

## `Stepper28BYJ48`

```python
motor.cw()
motor.ccw()
motor.stop()
motor.lock()
```

# Ejemplo mínimo

```python
from machine import Pin, I2C
from pca9685_28byj48 import PCA9685Board

i2c = I2C(
    0,
    scl=Pin(35),
    sda=Pin(33),
    freq=400_000
)

board = PCA9685Board(i2c, 0x40, -1)
board.set_speed(10)

motor = board.motor(0)
motor.cw()
```

Para cambiar de sentido:

```python
motor.ccw()
```

Para dejarlo libre:

```python
motor.stop()
```

Para mantenerlo bloqueado:

```python
motor.lock()
```

---

**Estado de la biblioteca:** probado con éxito con cuatro motores 28BYJ-48 funcionando simultáneamente en dos PCA9685.
