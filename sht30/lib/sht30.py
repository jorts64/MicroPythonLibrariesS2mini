# Jordi Orts 2026
# Válida para SHT30, SHT31, SHT35


from time import sleep_ms

class SHT30:
    # Repetibilidad: "high", "medium" o "low"
    _COMMANDS = {
        "high":   (0x2C, 0x06, 16),
        "medium": (0x2C, 0x0D,  7),
        "low":    (0x2C, 0x10,  5),
    }

    def __init__(self, i2c, address=0x45, repeatability="high"):
        self.i2c = i2c
        self.address = address
        self.repeatability = repeatability

        self._temperature = None
        self._humidity = None

        if repeatability not in self._COMMANDS:
            raise ValueError("repeatability: high, medium o low")

        # Reinicio inicial
        self.soft_reset()

    @staticmethod
    def _crc8(data):
        crc = 0xFF

        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x31) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF

        return crc

    def _command(self, msb, lsb):
        self.i2c.writeto(self.address, bytes((msb, lsb)))

    def soft_reset(self):
        self._command(0x30, 0xA2)
        sleep_ms(2)
        self._temperature = None
        self._humidity = None

    def measure(self):
        msb, lsb, delay = self._COMMANDS[self.repeatability]
        self._command(msb, lsb)
        sleep_ms(delay)

        data = self.i2c.readfrom(self.address, 6)

        # CRC de temperatura
        if self._crc8(data[0:2]) != data[2]:
            raise OSError("CRC de temperatura incorrecto")

        # CRC de humedad
        if self._crc8(data[3:5]) != data[5]:
            raise OSError("CRC de humedad incorrecto")

        temp_raw = (data[0] << 8) | data[1]
        humi_raw = (data[3] << 8) | data[4]

        self._temperature = 175.0 * temp_raw / 65535.0 - 45.0
        self._humidity = 100.0 * humi_raw / 65535.0

        return self._temperature, self._humidity

    @property
    def temperature(self):
        return self._temperature

    @property
    def humidity(self):
        return self._humidity

    def read_status(self):
        self._command(0xF3, 0x2D)
        sleep_ms(2)

        data = self.i2c.readfrom(self.address, 3)

        if self._crc8(data[0:2]) != data[2]:
            raise OSError("CRC del estado incorrecto")

        return (data[0] << 8) | data[1]

    def clear_status(self):
        self._command(0x30, 0x41)

    def heater(self, enabled=True):
        if enabled:
            self._command(0x30, 0x6D)
        else:
            self._command(0x30, 0x66)
