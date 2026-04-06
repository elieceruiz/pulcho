import time
import traceback

print("🚨 BOOT: iniciando worker (antes de imports)")

try:
    from ynab_client import get_transactions
    from processor import (
        to_dataframe,
        get_consumos,
        agregar_hora,
        agregar_datetime_real,
        horas_sin_consumo
    )
    from notifier import enviar_notificacion
except Exception as e:
    print("❌ ERROR EN IMPORTS:")
    print(str(e))
    print(traceback.format_exc())
    time.sleep(30)
    raise


INTERVALO = 300  # 5 minutos


def calcular_horas():
    print("📡 Obteniendo transacciones desde YNAB...")

    try:
        txs = get_transactions()
    except Exception as e:
        print("❌ Error consultando YNAB:", e)
        print(traceback.format_exc())
        return None

    if not txs:
        print("⚠️ No se recibieron transacciones")
        return None

    try:
        df = to_dataframe(txs)

        consumos = get_consumos(df)
        consumos = agregar_hora(consumos)
        consumos = agregar_datetime_real(consumos)

        if not consumos.empty and "datetime" in consumos.columns:
            ultimos = consumos.sort_values("datetime", ascending=False).head(3)
            print("\n🧾 Últimos consumos detectados:")
            print(ultimos[["memo", "datetime"]].to_string(index=False))
        else:
            print("\n⚠️ No hay consumos detectados")

        return horas_sin_consumo(consumos)

    except Exception as e:
        print("❌ Error procesando datos:", e)
        print(traceback.format_exc())
        return None


def main():
    print("🔥 WORKER INICIADO EN RENDER")
    print(f"⏱️ Intervalo: {INTERVALO}s\n")

    ultima_hora_notificada = None

    while True:
        inicio = time.time()
        print("🔁 Ejecutando ciclo...\n")

        try:
            horas = calcular_horas()

            if horas is None:
                print("⚠️ No se pudo calcular horas (error controlado)")
            else:
                horas_int = max(0, int(round(horas)))

                print(f"⏱️ Horas sin consumo: {horas:.2f}")

                if horas_int > 0 and horas_int != ultima_hora_notificada:
                    mensaje = f"Llevas {horas_int}h sin consumo. Vas bien."

                    try:
                        print("📤 Enviando notificación...")
                        enviar_notificacion(mensaje)
                        print("✅ Notificación enviada")
                        ultima_hora_notificada = horas_int
                    except Exception as e:
                        print("❌ Error enviando notificación:", e)
                        print(traceback.format_exc())
                else:
                    print("ℹ️ No se envía notificación")

        except Exception as e:
            print("❌ ERROR CRÍTICO EN LOOP")
            print(str(e))
            print(traceback.format_exc())

        duracion = round(time.time() - inicio, 2)
        print(f"⏱️ Ciclo tomó: {duracion}s")
        print(f"⏳ Esperando {INTERVALO}s...\n")

        time.sleep(INTERVALO)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("💥 ERROR FATAL (main murió):")
        print(str(e))
        print(traceback.format_exc())
        time.sleep(60)