import os
import time
from colorama import Fore


def print_e(msg):
    print(Fore.RED+ msg +Fore.RESET)


def print_w(msg):
    print(Fore.YELLOW+ msg +Fore.RESET)


scripts = ["farmacia_Del_Ahorro.py", "farmacia_guadalajara.py", "farmacias_benavides.py", "farmacias_San_Pablo.py"]

for script in scripts:
    print(f"///////////////++++++++++++++++++++++ ejecutando {script} ++++++++++++++++++++++////////////////")
    os.system(f"python {script}")

    print("Esperando para siguiente ejecución.")
    print("<----------")
    time.sleep(1)
    print("<---------")
    time.sleep(1)
    print("<--------")
    time.sleep(1)
    print("<-------")
    time.sleep(1)
    print("<------")
    time.sleep(1)
    print("<-----")
    time.sleep(1)
    print("<----")
    time.sleep(1)
    print("<---")
    time.sleep(1)
    print("<--")
    time.sleep(1)
    print("<-")
    time.sleep(1)

print("///////////////////////++++++++++++++++++++++ FIN DE LA EJECUCION DE LOS SCRAPPERS ++++++++++++++++++++++////////////////")