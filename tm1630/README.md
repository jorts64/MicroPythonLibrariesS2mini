# MóDULO DE TECLADO + 8 LEDS + 8 DÍGITOS DE 7 SEGMENTOS CON TM1638

## Agradecimientos

la librería original es obra de [Mike Causer](https://github.com/mcauser/micropython-tm1638), compartida bajo licencia MIT, como este repositorio, y al que se le reconoce su autoría (Es de bien nacidos ser agradecidos)

## El módulo standard de 8 botones

![](tm1638-001.png)


![](tm1638-002.png)

![](tm1638-003.png)

## Módulo de 16 botones

![](tm1638-16buttons.png)


## Mejoras

### Extensión a módulo de 16 botones

Si bien la librería de Mike Causer implementa una función para leer los 16 botones, el mapeo de los segmentos en este módulo es diferente y se representan mal las fuentes. Se ha añadido un parámetro a la creación del objeto para especificar el uso de este módulo y representar las fuentes correctamente. Ejemplos:

Para el módulo de 16 botones:

~~~
tm = tm1638.TM1638(stb=Pin(16), clk=Pin(15), dio=Pin(14), display_layout="matrix")
~~~


Para el módulo de 8 botones no es necesario poner este parámetro, para compatibilidad con la librería de Mike Causer, tomando el valor por defecto *standard* :

~~~
tm = tm1638.TM1638(stb=Pin(16), clk=Pin(15), dio=Pin(14))
~~~



Además se ha unificado la lectura de los botones en un único método en función de ese mismo parámetro:

~~~
print(tm.keys(),)
~~~



## Números decimales

He añadido a la libreria una función que permite representar números con decimales:

~~~
    def decimal(self, num, decimals=1, pos=0):
        """Muestra un número decimal en el display.
        num: número a mostrar
        decimals: número de cifras decimales
        pos: posición inicial (0-7)
        """
        string = "{:.{}f}".format(num, decimals)
        self.segments(self.encode_string(string), pos)
~~~

Uso:

~~~
tm.decimal(12.6, 1, 4)    # 12.6 empezando en la posición 4
tm.decimal(3.14159, 2, 0) # 3.14
tm.decimal(25, 2, 0)      # 25.00
tm.decimal(-7.5, 1, 0)    # -7.5
~~~