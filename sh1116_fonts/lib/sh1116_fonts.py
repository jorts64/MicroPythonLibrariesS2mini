
# MicroPython SH1116 OLED driver
# Basado en la API del driver ssd1306_fonts
#
# Interfaces I2C y SPI.
# Framebuffer de 1 bit.
#
# Compatible con paneles SH1116 de 128x64 y 128x32,
# siempre que la configuracion de direccionamiento del modulo
# coincida con los parametros del driver.

import time
import framebuf
from array import array

# Comandos SH1116
SET_CONTRAST = const(0x81)
SET_DISP = const(0xAE)
SET_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_COM_OUT_DIR = const(0xC0)
SET_NORMAL = const(0xA6)
SET_INVERSE = const(0xA7)
SET_DC_DC = const(0xAD)
SET_DISP_OFFSET = const(0xD3)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_MUX_RATIO = const(0xA8)

class SH1116:
    def __init__(self, width, height, external_vcc=False,
                 col_offset=2):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = height // 8
        self.col_offset = col_offset

        # La subclase debe crear self.framebuf antes de llamar
        # a esta inicializacion.
        self.poweron()
        self.init_display()


    def init_display(self):
        for cmd in (
            0xAE,
            0xD5, 0x80,
            0xA8, 0x3F,
            0xD3, 0x00,
            0x40,
            0xAD, 0x8B,
            0xA1,
            0xC8,
            0xDA, 0x12,
            0x81, 0x7F,
            0xD9, 0x22,
            0xDB, 0x35,
            0xA6,
            0xA4,
        ):
            self.write_cmd(cmd)

        self.fill(0)
        self.show()
        self.write_cmd(0xAF)



    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        pass

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast & 0xFF)

    def invert(self, invert):
        self.write_cmd(SET_INVERSE if invert else SET_NORMAL)


#     def show(self):
#         for page in range(self.pages):
#             self.write_cmd(0xB0 | page)
#             self.write_cmd(0x02)  # Columna baja
#             self.write_cmd(0x10)  # Columna alta
# 
#             start = page * self.width
#             end = start + self.width
#             self.write_framebuf_page(start, end)



    def show(self):
        for page in range(self.pages):
            # Una sola transaccion para los tres comandos
            cmds = bytearray(6)
            cmds[0] = 0x80
            cmds[1] = 0xB0 | page
            cmds[2] = 0x80
            cmds[3] = 0x02
            cmds[4] = 0x80
            cmds[5] = 0x10

            self.write_cmd_block(cmds)

            start = page * self.width
            end = start + self.width
            self.write_framebuf_page(start, end)


    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col=None):
        if col is None:
            return self.framebuf.pixel(x, y)
        self.framebuf.pixel(x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def ellipse(self, x, y, rx, ry, col=1, f=False):
        self.framebuf.ellipse(x, y, rx, ry, col, f)

    def line(self, x1, y1, x2, y2, col=1):
        self.framebuf.line(x1, y1, x2, y2, col)

    def hline(self, x, y, w, col=1):
        self.framebuf.hline(x, y, w, col)

    def fill_rect(self, x, y, w, h, col=1):
        self.framebuf.fill_rect(x, y, w, h, col)

    def poly(self, x, y, coords, col=1, f=False):
        if not isinstance(coords, array):
            coords = array('h', coords)
        self.framebuf.poly(x, y, coords, col, f)

    def rect(self, x, y, w, h, col=1, f=False):
        self.framebuf.rect(x, y, w, h, col, f)

    def vline(self, x, y, h, col=1):
        self.framebuf.vline(x, y, h, col)

    def blit(self, fbuf, x, y, key=-1, palette=None):
        self.framebuf.blit(fbuf, x, y, key, palette)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)

    def draw_text(self, text, x, y, font):
        cx = x

        for ch in text:
            glyph = ord(ch)

            if glyph < font.FIRST or glyph > font.LAST:
                continue

            self._draw_glyph(glyph, cx, y, font)
            cx += font.WIDTH

    def charset(self, font, pausa=1):
        cols = self.width // font.WIDTH
        rows = self.height // font.HEIGHT

        if cols == 0 or rows == 0:
            return

        chars_per_page = cols * rows
        total = font.LAST - font.FIRST + 1
        pos = 0

        while pos < total:
            self.fill(0)

            for row in range(rows):
                for col in range(cols):
                    index = pos + row * cols + col

                    if index >= total:
                        break

                    glyph = font.FIRST + index
                    self.draw_text(
                        chr(glyph),
                        col * font.WIDTH,
                        row * font.HEIGHT,
                        font
                    )

            self.show()
            pos += chars_per_page

            if pos < total:
                time.sleep(pausa)

    def _draw_glyph(self, glyph, x, y, font):
        # Se presupone que _FONT contiene un byte por fila
        # de cada glifo, como en la libreria original.
        index = (glyph - font.FIRST) * font.HEIGHT

        for row in range(font.HEIGHT):
            line = font._FONT[index + row]

            for col in range(font.WIDTH):
                if line & (0x80 >> col):
                    self.pixel(x + col, y + row, 1)


class SH1116_I2C(SH1116):
    def __init__(self, width, height, i2c, addr=0x3C,
                 external_vcc=False, col_offset=2):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)

        self.buffer = bytearray((height // 8) * width + 1)
        self.buffer[0] = 0x40

        self.framebuf = framebuf.FrameBuffer1(
            memoryview(self.buffer)[1:],
            width,
            height
        )

        self.cmd_page = bytearray(6)
        
        super().__init__(
            width, height, external_vcc, col_offset
        )

    def write_cmd(self, cmd):
        self.temp[0] = 0x80
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)




    def write_framebuf_page(self, start, end):
        view = memoryview(self.buffer)
        self.i2c.writevto(
            self.addr,
            (b"\x40", view[1 + start:1 + end])
        )


#     def write_framebuf_page(self, start, end):
#         view = memoryview(self.buffer)
#         packet = bytearray(end - start + 1)
#         packet[0] = 0x40
#         packet[1:] = view[1 + start:1 + end]
#         self.i2c.writeto(self.addr, packet)


    def write_framebuf(self):
        self.i2c.writeto(self.addr, self.buffer)



    def write_cmd_block(self, cmds):
        self.i2c.writeto(self.addr, cmds)



class SH1116_SPI(SH1116):
    def __init__(self, width, height, spi, dc, res, cs,
                 external_vcc=False, col_offset=2):
        self.rate = 10 * 1024 * 1024

        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)

        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs

        self.buffer = bytearray((height // 8) * width)
        self.framebuf = framebuf.FrameBuffer1(
            self.buffer, width, height
        )

        super().__init__(
            width, height, external_vcc, col_offset
        )

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.high()
        self.dc.low()
        self.cs.low()
        self.spi.write(bytes([cmd]))
        self.cs.high()

    def write_framebuf_page(self, start, end):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.high()
        self.dc.high()
        self.cs.low()
        self.spi.write(memoryview(self.buffer)[start:end])
        self.cs.high()

    def write_framebuf(self):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs.high()
        self.dc.high()
        self.cs.low()
        self.spi.write(self.buffer)
        self.cs.high()

    def poweron(self):
        self.res.high()
        time.sleep_ms(1)
        self.res.low()
        time.sleep_ms(10)
        self.res.high()
