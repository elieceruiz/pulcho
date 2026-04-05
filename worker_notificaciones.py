# worker_notificaciones.py

import time
import pandas as pd

from ynab_client import get_transactions
from processor import (
    to_dataframe,
    get_consumos,
    agregar_hora,
    agregar_datetime_real,
    horas_sin_consumo
)
from notifier import enviar_notificacion


INTERVALO = 300  # 5 minutos


def calcular_horas():
    txs = get_transactions()
    df = to_dataframe(txs)

    consumos = get_consumos(df)
    consumos = agregar_hora(consumos)
    consumos = agregar_datetime_real(consumos)

    return horas_sin_consumo(consumos)


def main():
    ultima_hora_notificada = -1

    while True:
        try:
            horas = calcular_horas()
            horas_int = int(horas)

            print(f"Horas sin consumo: {horas:.2f}")

            if horas_int > 0 and horas_int != ultima_hora_notificada:
                mensaje = f"Llevas {horas_int}h sin consumo. Vas bien."
                enviar_notificacion(mensaje)

                print("🔔 Notificación enviada")

                ultima_hora_notificada = horas_int

        except Exception as e:
            print("Error:", e)

        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()