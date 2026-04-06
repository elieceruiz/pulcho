# worker_notificaciones.py

import time
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


INTERVALO = 120  # 🔥 2 minutos (pruebas)


def calcular_horas():
    print("📡 Obteniendo transacciones desde YNAB...", flush=True)

    try:
        txs = get_transactions()
    except Exception as e:
        print("❌ Error consultando YNAB:", flush=True)
        print(str(e), flush=True)
        print(traceback.format_exc(), flush=True)
        return None

    if not txs:
        print("⚠️ No se recibieron transacciones", flush=True)
        return None

    try:
        df = to_dataframe(txs)

        consumos = get_consumos(df)
        consumos = agregar_hora(consumos)
        consumos = agregar_datetime_real(consumos)

        if not consumos.empty and "datetime" in consumos.columns:
            ultimos = consumos.sort_values("datetime", ascending=False).head(3)
            print("\n🧾 Últimos consumos detectados:", flush=True)
            print(ultimos[["memo", "datetime"]].to_string(index=False), flush=True)
        else:
            print("\n⚠️ No hay consumos detectados", flush=True)

        return horas_sin_consumo(consumos)

    except Exception as e:
        print("❌ Error procesando datos:", flush=True)
        print(str(e), flush=True)
        print(traceback.format_exc(), flush=True)
        return None


def main():
    print("🔥 WORKER INICIADO", flush=True)
    print(f"⏱️ Intervalo: {INTERVALO}s\n", flush=True)

    while True:
        inicio = time.time()
        print("🔁 Ejecutando ciclo...\n", flush=True)

        try:
            horas = calcular_horas()

            if horas is None:
                print("⚠️ No se pudo calcular horas", flush=True)
            else:
                horas_int = max(0, int(horas))

                print(f"⏱️ Horas sin consumo: {horas:.2f}", flush=True)

                # 🔥 MODO PRUEBA: SIEMPRE ENVÍA (cada 2 minutos)
                if horas_int > 0:
                    mensaje = f"Llevas {horas_int}h sin consumo. Vas bien."

                    try:
                        print("📤 Enviando notificación...", flush=True)
                        enviar_notificacion(mensaje)
                        print("✅ Notificación enviada", flush=True)

                    except Exception as e:
                        print("❌ Error enviando notificación:", flush=True)
                        print(str(e), flush=True)
                        print(traceback.format_exc(), flush=True)

                else:
                    print("ℹ️ No se envía notificación", flush=True)

        except Exception as e:
            print("💥 ERROR CRÍTICO EN LOOP:", flush=True)
            print(str(e), flush=True)
            print(traceback.format_exc(), flush=True)

        duracion = round(time.time() - inicio, 2)
        print(f"⏱️ Ciclo tomó: {duracion}s", flush=True)
        print(f"⏳ Esperando {INTERVALO}s...\n", flush=True)

        time.sleep(INTERVALO)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("💀 ERROR FATAL:", flush=True)
        print(str(e), flush=True)
        print(traceback.format_exc(), flush=True)
        time.sleep(60)