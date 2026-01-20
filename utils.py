import random
import string


def gerar_codigo_curto():
    caracteres = string.ascii_letters + string.digits
    codigo = ''.join(random.choices(caracteres, k=6))
    return codigo