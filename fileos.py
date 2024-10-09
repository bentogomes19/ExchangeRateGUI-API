import os
import sys

def resource_path(relative_path):
    try:
        #    PyInstaller cria uma pasta temporária e armazena o caminho nesse atributo
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
        