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

    # 🔥 DEBUG (NO rompe nada)
    if not consumos.empty:
        ultimos = consumos.sort_values("datetime", ascending=False).head(3)
        print("\n🧾 Últimos consumos detectados:")
        print(ultimos[["memo", "datetime"]])
    else:
        print("\n⚠️ No hay consumos detectados")

    return horas_sin_consumo(consumos)


def main():
    ultima_hora_notificada = None

    while True:
        try:
            horas = calcular_horas()
            horas_int = int(horas)

            print(f"\n⏱️ Horas sin consumo: {horas:.2f}")

            if horas_int > 0 and horas_int != ultima_hora_notificada:
                mensaje = f"Llevas {horas_int}h sin consumo. Vas bien."

                print("📤 Enviando notificación...")
                enviar_notificacion(mensaje)

                ultima_hora_notificada = horas_int

        except Exception as e:
            print("❌ Error en worker:", e)

        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
