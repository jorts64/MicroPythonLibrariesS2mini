
# menu_oled.py
# Sistema de menus para SH1116_I2C y EncoderKnob
# Pantalla 128x64, fuente 8x16, cuatro opciones visibles.

import time

class MenuOLED:

    def __init__(self, oled, enc, font,
                 root=0, rows=4, line_height=16):
        self.oled = oled
        self.enc = enc
        self.font = font
        self.root = root
        self.rows = rows
        self.line_height = line_height

        self.menus = {}
        self.selected = {}
        self.first_visible = {}

        self.current = root
        self.stack = []
        self.started = False

        self.debounce_ms = 300
        self.last_press_ms = time.ticks_ms()
        
        self.editor = None
        
        self.disabled = False
        self.custom_rotated = None
        self.custom_pressed = None

    def add(self, menu_id, position, text,
            callback=None, submenu=None):
        """Anade una opcion a un menu."""

        if menu_id not in self.menus:
            self.menus[menu_id] = []

        items = self.menus[menu_id]

        item = {
            "position": position,
            "text": str(text),
            "callback": callback,
            "submenu": submenu
        }

        # Sustituir la opcion si ya existe esa posicion.
        replaced = False

        for i in range(len(items)):
            if items[i]["position"] == position:
                items[i] = item
                replaced = True
                break

        if not replaced:
            items.append(item)

        items.sort(key=lambda x: x["position"])

        self.selected.setdefault(menu_id, 0)
        self.first_visible.setdefault(menu_id, 0)

        if self.started and menu_id == self.current:
            self.draw()

    def start(self):
        """Iniciar mostrando el menu raiz."""

        if self.root not in self.menus:
            raise ValueError("No existe el menu raiz")

        if not self.menus[self.root]:
            raise ValueError("El menu raiz esta vacio")

        self.current = self.root
        self.stack = []
        self.started = True

        self.draw()

    def selmenu(self, menu_id):
        """Cambiar de menu desde cualquier funcion."""

        if menu_id not in self.menus:
            raise ValueError("El menu no existe")

        if not self.menus[menu_id]:
            raise ValueError("El menu esta vacio")

        if menu_id == self.root:
            self.stack = []

        elif menu_id != self.current:
            self.stack.append(self.current)

        self.current = menu_id

        self.selected.setdefault(menu_id, 0)
        self.first_visible.setdefault(menu_id, 0)

        self._ensure_visible()

        if self.started:
            self.draw()


    def rotated(self, delta):
        """Girar para navegar o modificar un valor."""

        if not self.started or delta == 0:
            return

        if self.disabled:
            if self.custom_rotated is not None:
                self.custom_rotated(delta)
            return

        # Si estamos editando un numero.
        if self.editor is not None:
            number = self.editor["number"]

            value = number["value"]
            value += int(delta) * number["step"]

            value = max(
                number["minimum"],
                min(number["maximum"], value)
            )

            number["value"] = value
            self.draw()
            return

        # Navegacion normal.
        items = self.menus.get(self.current, [])

        if not items:
            return

        index = self.selected.get(self.current, 0)
        index = (index + int(delta)) % len(items)

        self.selected[self.current] = index

        self._ensure_visible()
        self.draw()



    def pressed(self):
        """Callback del boton con antirrebote por tiempo."""

        if not self.started:
            return

        now = time.ticks_ms()

        # Ignorar pulsaciones demasiado proximas.
        if time.ticks_diff(now, self.last_press_ms) < self.debounce_ms:
            return

        self.last_press_ms = now

        if self.disabled:
            if self.custom_pressed is not None:
                self.custom_pressed()
            return

        # Si estamos editando, el boton confirma el valor.
        if self.editor is not None:
            editor = self.editor
            number = editor["number"]
            value = number["value"]

            self.editor = None

            callback = number["callback"]

            if callback is not None:
                callback()

                if self.started:
                    self.draw()

            return

        items = self.menus.get(self.current, [])

        if not items:
            return

        index = self.selected.get(self.current, 0)
        item = items[index]

        # Si es una opcion numerica, entrar en el editor.
        if item.get("number") is not None:
            self.editor = item
            self.draw()
            return

        # Abrir sub menu.
        if item["submenu"] is not None:
            self.selmenu(item["submenu"])
            return

        # Posicion cero sin callback = volver.
        if (self.current != self.root
                and item["position"] == 0
                and item["callback"] is None):
            self.back()
            return

        # Ejecutar la accion.
        callback = item["callback"]

        if callback is not None:
            callback()

            if self.started and not self.disabled:
                self.draw()


    def back(self):
        """Volver al menu anterior."""

        if self.current == self.root:
            return

        if self.stack:
            self.current = self.stack.pop()
        else:
            self.current = self.root

        self._ensure_visible()

        if self.started:
            self.draw()

    def _ensure_visible(self):
        """Mantener la seleccion dentro de las cuatro lineas."""

        items = self.menus.get(self.current, [])

        if not items:
            self.first_visible[self.current] = 0
            return

        index = self.selected.get(self.current, 0)
        first = self.first_visible.get(self.current, 0)

        if index < first:
            first = index

        elif index >= first + self.rows:
            first = index - self.rows + 1

        max_first = max(0, len(items) - self.rows)

        first = max(0, min(first, max_first))

        self.first_visible[self.current] = first

    def draw(self):
        """Dibujar las opciones y la flecha de seleccion."""

        items = self.menus.get(self.current, [])

        self.oled.fill(0)


        # Pantalla de edicion numerica.
        if self.editor is not None:
            number = self.editor["number"]
            value = number["value"]
            label = self.editor["text"][:16]

            value_text = str(value)

            self.oled.draw_text(
                label, 0, 0, self.font
            )

            # Centrar el valor numerico.
            x = max(0, (128 - len(value_text) * 8) // 2)

            self.oled.draw_text(
                value_text, x, 16, self.font
            )

            self.oled.draw_text(
                "Girar:cambiar", 0, 32, self.font
            )

            self.oled.draw_text(
                "Pulsar:aceptar", 0, 48, self.font
            )

            self.oled.show()
            return


        selected = self.selected.get(self.current, 0)
        first = self.first_visible.get(self.current, 0)

        # 128 px / 8 px por caracter = 16 caracteres.
        # Reservamos el primero para la flecha.
        max_chars = 15

        for row in range(self.rows):
            index = first + row

            if index >= len(items):
                break

            item = items[index]
            text = item["text"][:max_chars]

            y = row * self.line_height

            if index == selected:
                marker = ">"
            else:
                marker = " "

            self.oled.draw_text(marker, 0, y, self.font)
            self.oled.draw_text(text, 8, y, self.font)

        self.oled.show()


    def add_number(self, menu_id, position, text, value,
                   minimum, maximum, step=1, callback=None):
        """Crear una opcion que permite editar un valor numerico."""

        if step <= 0:
            raise ValueError("step debe ser mayor que cero")

        if minimum > maximum:
            raise ValueError("minimum no puede superar maximum")

        value = max(minimum, min(maximum, value))

        self.add(menu_id, position, text)

        items = self.menus[menu_id]

        for item in items:
            if item["position"] == position:
                item["number"] = {
                    "value": value,
                    "minimum": minimum,
                    "maximum": maximum,
                    "step": step,
                    "callback": callback
                }
                break



    def disable(self, rotated_callback, pressed_callback):
        """
        Desactiva temporalmente los menus y delega el encoder
        a dos funciones de la aplicacion.
        """

        self.custom_rotated = rotated_callback
        self.custom_pressed = pressed_callback
        self.disabled = True


    def restore(self):
        """
        Recupera el sistema de menus en el punto donde se abandono.
        """

        self.disabled = False
        self.custom_rotated = None
        self.custom_pressed = None

        # Conserva el menu y la opcion seleccionada.
        self.draw()

