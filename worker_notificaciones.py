import time
import pandas as pd
import traceback

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
TZ = "America/Bogota"


def calcular_horas():
    print("📡 Obteniendo transacciones desde YNAB...")

    try:
        txs = get_transactions()
    except Exception as e:
        print("❌ Error consultando YNAB:", e)
        return 0

    if not txs:
        print("⚠️ No se recibieron transacciones")
        return 0

    df = to_dataframe(txs)

    consumos = get_consumos(df)
    consumos = agregar_hora(consumos)
    consumos = agregar_datetime_real(consumos)

    # 🔥 DEBUG CLARO
    if not consumos.empty and "datetime" in consumos.columns:
        ultimos = consumos.sort_values("datetime", ascending=False).head(3)
        print("\n🧾 Últimos consumos detectados:")
        print(ultimos[["memo", "datetime"]].to_string(index=False))
    else:
        print("\n⚠️ No hay consumos detectados")

    return horas_sin_consumo(consumos)


def main():
    print("🔥 WORKER INICIADO EN RENDER")
    print(f"⏱️ Intervalo configurado: {INTERVALO} segundos\n")

    ultima_hora_notificada = None

    while True:
        print("🔁 Ejecutando ciclo...\n")

        try:
            horas = calcular_horas()
            horas_int = int(horas)

            print(f"⏱️ Horas sin consumo: {horas:.2f}")

            # ✅ ENVÍO CONTROLADO (no spam)
            if horas_int > 0 and horas_int != ultima_hora_notificada:
                mensaje = f"Llevas {horas_int}h sin consumo. Vas bien."

                print("📤 Enviando notificación...")
                enviar_notificacion(mensaje)

                print("✅ Notificación enviada correctamente")
                ultima_hora_notificada = horas_int
            else:
                print("ℹ️ No se envía notificación")

        except Exception as e:
            print("\n❌ ERROR EN WORKER")
            print(str(e))
            print(traceback.format_exc())

        print(f"\n⏳ Esperando {INTERVALO} segundos...\n")
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()