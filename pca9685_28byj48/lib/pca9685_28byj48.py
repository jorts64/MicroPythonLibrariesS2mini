from machine import Pin
import time


class PCA9685Board:
    """
    PCA9685 + hasta 4 motores 28BYJ-48.

    Cada PCA9685 controla hasta 4 motores.

    Los cuatro motores de una misma placa comparten
    la frecuencia/velocidad.

    Cada placa puede tener una velocidad diferente.

    Parámetros:

        i2c      -> objeto machine.I2C
        address  -> dirección I2C del PCA9685
        oe_pin   -> GPIO conectado a OE.
                    -1 significa que OE no está conectado.
    """

    # --------------------------------------------------------
    # Registros PCA9685
    # --------------------------------------------------------

    MODE1 = 0x00
    MODE2 = 0x01
    PRESCALE = 0xFE

    LED0_ON_L = 0x06

    # --------------------------------------------------------
    # Constantes
    # --------------------------------------------------------

    OSCILLATOR = 25_000_000

    STEPS_PER_REV = 4096

    # Un ciclo PWM corresponde a 8 pasos half-step
    STEPS_PER_PWM = 8

    # --------------------------------------------------------
    # Constructor
    # --------------------------------------------------------

    def __init__(self, i2c, address=0x40, oe_pin=-1):

        self.i2c = i2c
        self.address = address

        # OE opcional
        self.oe_pin = oe_pin

        if oe_pin >= 0:
            self.oe = Pin(
                oe_pin,
                Pin.OUT,
                value=0
            )
        else:
            self.oe = None

        # Motores
        self.motors = []

        for n in range(4):
            self.motors.append(
                Stepper28BYJ48(self, n)
            )

        self.rpm = 0

        self._init_pca9685()


    # ========================================================
    # I2C
    # ========================================================

    def _write8(self, reg, value):

        self.i2c.writeto_mem(
            self.address,
            reg,
            bytes([value & 0xFF])
        )


    def _read8(self, reg):

        return self.i2c.readfrom_mem(
            self.address,
            reg,
            1
        )[0]


    # ========================================================
    # INICIALIZACIÓN
    # ========================================================

    def _init_pca9685(self):

        # MODE1:
        # AI = Auto Increment
        self._write8(
            self.MODE1,
            0x20
        )

        # MODE2:
        # OUTDRV = Totem pole
        self._write8(
            self.MODE2,
            0x04
        )

        # Motor parado
        self.stop_all()


    # ========================================================
    # VELOCIDAD
    # ========================================================

    def set_speed(self, rpm):

        """
        Establece la velocidad de todos los motores
        de esta placa.

        rpm:
            revoluciones por minuto.
        """

        if rpm < 0:
            rpm = -rpm

        if rpm == 0:
            self.rpm = 0
            self.stop_all()
            return 0

        # Pasos por segundo
        steps_per_second = (
            rpm * self.STEPS_PER_REV
        ) / 60.0

        # Cada ciclo PWM genera 8 pasos
        pwm_frequency = (
            steps_per_second /
            self.STEPS_PER_PWM
        )

        real_frequency = self._set_pwm_frequency(
            pwm_frequency
        )

        # Velocidad real resultante
        real_rpm = (
            real_frequency *
            self.STEPS_PER_PWM *
            60
        ) / self.STEPS_PER_REV

        self.rpm = real_rpm

        return real_rpm


    # ========================================================
    # FRECUENCIA PWM
    # ========================================================

    def _set_pwm_frequency(self, frequency):

        if frequency < 1:
            frequency = 1

        if frequency > 1526:
            frequency = 1526

        prescale = int(
            (
                self.OSCILLATOR /
                (4096 * frequency)
            ) - 1 + 0.5
        )

        old_mode = self._read8(
            self.MODE1
        )

        # Sleep
        self._write8(
            self.MODE1,
            (old_mode & 0x7F) | 0x10
        )

        # Prescaler
        self._write8(
            self.PRESCALE,
            prescale
        )

        # Wake up
        self._write8(
            self.MODE1,
            old_mode
        )

        time.sleep_ms(1)

        # Restart + Auto Increment
        self._write8(
            self.MODE1,
            old_mode | 0xA0
        )

        # Frecuencia real
        return self.OSCILLATOR / (
            4096 * (prescale + 1)
        )


    # ========================================================
    # CANALES
    # ========================================================

    def _set_channel(self, channel, on, off):

        reg = self.LED0_ON_L + channel * 4

        data = bytes((
            on & 0xFF,
            (on >> 8) & 0x0F,
            off & 0xFF,
            (off >> 8) & 0x0F
        ))

        self.i2c.writeto_mem(
            self.address,
            reg,
            data
        )


    def _channel_off(self, channel):

        reg = self.LED0_ON_L + channel * 4

        data = bytes((
            0x00,
            0x00,
            0x00,
            0x10
        ))

        self.i2c.writeto_mem(
            self.address,
            reg,
            data
        )


    # ========================================================
    # MOTOR
    # ========================================================

    def motor(self, number):

        if number < 0 or number > 3:
            raise ValueError(
                "Motor debe ser 0..3"
            )

        return self.motors[number]


    # ========================================================
    # PARAR TODOS
    # ========================================================

    def stop_all(self):

        for motor in self.motors:
            motor.stop()


    # ========================================================
    # BLOQUEAR TODOS
    # ========================================================

    def lock_all(self):

        for motor in self.motors:
            motor.lock()


    # ========================================================
    # OE
    # ========================================================

    def oe_on(self):

        """
        Habilita las salidas.

        Si OE no está conectado, no hace nada.
        """

        if self.oe is not None:
            self.oe.value(0)


    def oe_off(self):

        """
        Deshabilita todas las salidas.

        Si OE no está conectado, no hace nada.
        """

        if self.oe is not None:
            self.oe.value(1)


    def oe_connected(self):

        return self.oe is not None


# =================================================================
# 28BYJ-48
# =================================================================

class Stepper28BYJ48:

    def __init__(self, board, number):

        self.board = board
        self.number = number
        self.base_channel = number * 4

        self.direction = 0
        self.running = False


    def cw(self):

        self._configure(True)

        self.direction = 1
        self.running = True


    def ccw(self):

        self._configure(False)

        self.direction = -1
        self.running = True


    def stop(self):

        for ch in range(
            self.base_channel,
            self.base_channel + 4
        ):
            self.board._channel_off(ch)

        self.direction = 0
        self.running = False


    def lock(self):

        # Primera fase activada
        self.board._set_channel(
            self.base_channel + 0,
            0,
            4095
        )

        for ch in range(
            self.base_channel + 1,
            self.base_channel + 4
        ):
            self.board._channel_off(ch)

        self.direction = 0
        self.running = False


    def _configure(self, clockwise):

        a = self.base_channel + 0
        b = self.base_channel + 1
        c = self.base_channel + 2
        d = self.base_channel + 3

        if clockwise:

            self.board._set_channel(a, 3584, 1024)
            self.board._set_channel(b, 512, 2048)
            self.board._set_channel(c, 1536, 3072)
            self.board._set_channel(d, 2560, 0)

        else:

            self.board._set_channel(a, 3584, 1024)
            self.board._set_channel(d, 512, 2048)
            self.board._set_channel(c, 1536, 3072)
            self.board._set_channel(b, 2560, 0)

