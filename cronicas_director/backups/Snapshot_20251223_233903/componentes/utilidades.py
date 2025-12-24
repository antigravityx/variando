# componentes/utilidades.py
import msvcrt
import sys
import locale
from num2words import num2words

from componentes.colores import Colors

def get_color_for_usage(usage):
    """Devuelve un color basado en el porcentaje de uso."""
    if usage > 75:
        return Colors.RED
    elif usage > 40:
        return Colors.YELLOW
    else:
        return Colors.GREEN

def get_color_for_mem_mb(mem_mb):
    """Devuelve un color basado en el uso de memoria en MB."""
    if mem_mb > 500:
        return Colors.RED
    elif mem_mb > 100:
        return Colors.YELLOW
    else:
        return Colors.GREEN

def input_con_mascara(prompt=""):
    """Input personalizado que oculta parcialmente los caracteres (Patrón: * * -)."""
    print(prompt, end='', flush=True)
    buf = ""
    while True:
        ch = msvcrt.getwch()
        if ch in {'\r', '\n'}:
            print('')
            return buf
        elif ch == '\x08': # Backspace
            if len(buf) > 0:
                buf = buf[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        elif ch == '\x03': # Ctrl+C
            raise KeyboardInterrupt
        else:
            if ch.isprintable():
                buf += ch
                # Mostrar 2, Ocultar 1 (Patrón: A B - D E -)
                if (len(buf)) % 3 == 0:
                    sys.stdout.write('-')
                else:
                    sys.stdout.write(ch)
                sys.stdout.flush()

def format_and_describe_number(number):
    """Formatea un número a un string con separadores y lo convierte a palabras en español."""
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
        except locale.Error:
            pass # Fallback to default formatting if locales fail
    formatted_number = locale.format_string('%.2f', number, grouping=True)
    parte_entera = int(number)
    parte_decimal = int(round((number - parte_entera) * 100))
    palabras_enteras = num2words(parte_entera, lang='es')
    palabras_decimales = num2words(parte_decimal, lang='es') if parte_decimal > 0 else "cero"
    descripcion = f"({palabras_enteras} con {palabras_decimales} centavos)"
    return formatted_number, descripcion