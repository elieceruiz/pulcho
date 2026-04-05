# app.py

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from ynab_client import get_transactions
from processor import *

# 🔹 FECHAS EN ESPAÑOL
MESES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

def formatear_fecha_es(fecha):
    return f"{fecha.day:02d} {MESES[fecha.month]} {fecha.year}"

def fmt_money(x):
    return f"${int(x):,}".replace(",", ".")


st.set_page_config(
    page_title="Pulcho",
    page_icon="🍻",
    layout="centered"
)

st.title("🍻 Pulcho")

st_autorefresh(interval=20000, key="refresh")

# 🔹 DATA
txs = get_transactions()
df = to_dataframe(txs)

consumos = get_consumos(df)
consumos = agregar_hora(consumos)
consumos = agregar_producto_limpio(consumos)
consumos = agregar_datetime_real(consumos)

carve = get_carve(df)
carve = agregar_hora(carve)  # ✅ AQUÍ SE AGREGA

# 🔹 MÉTRICAS
total = total_consumo(consumos)
horas = horas_sin_consumo(consumos)

resumen = resumen_carve(carve)

precio = resumen["precio_gramo"]
gramos_equivalentes = total / precio if precio else 0


# 🔹 TABS
tab_estado, tab_consumos, tab_carve = st.tabs(["Estado", "Consumos", "CARVE"])


# --- ESTADO ---
with tab_estado:
    
    st.markdown(f"## {round(horas, 1)}")
    st.caption("horas sin consumo")    

    st.write("")

    st.markdown(f"### {fmt_money(total)}")
    st.caption("acumulado en bebidas")

    st.write("")

    kg = round(gramos_equivalentes / 1000, 2) if precio else 0
    st.markdown(f"### {kg} kg")
    st.caption("equivalente en proteína")


# --- CONSUMOS ---
with tab_consumos:
    
    dias = st.number_input(
        "ventana (días)",
        min_value=0,
        max_value=30,
        value=0,
        step=1,
        help="0 = histórico completo"
    )

    if dias == 0:
        datos = consumos.copy()
        leyenda = "histórico completo"
    else:
        limite = pd.Timestamp.now() - pd.Timedelta(days=dias)
        datos = consumos[consumos["datetime"] >= limite]
        leyenda = f"últimos {dias} días"

    if len(datos) > 1:
        delta = datos["datetime"].sort_values().diff().dropna()
        frecuencia = delta.mean().total_seconds() / 3600
    else:
        frecuencia = 0

    st.markdown(f"### cada {round(frecuencia, 1)} horas")
    st.caption(f"frecuencia {leyenda}")

    st.write("")

    tabla = datos.sort_values("datetime", ascending=False).copy()

    tabla["Fecha"] = tabla["date"].apply(formatear_fecha_es)
    tabla["Hora"] = tabla["hora"]
    tabla["Producto"] = tabla["producto"]
    tabla["Valor"] = tabla["amount"].abs().apply(fmt_money)

    tabla = tabla[["Fecha", "Hora", "Producto", "Valor"]].reset_index(drop=True)
    tabla.index = range(len(tabla), 0, -1)

    st.dataframe(tabla)


# --- CARVE ---
with tab_carve:
    
    if precio is not None:
        st.markdown(f"### ${round(precio, 2)} / g")
    else:
        st.markdown("### —")

    st.caption("precio actual estimado")

    st.write("")

    tabla = carve.sort_values("date", ascending=False).copy()

    tabla["Fecha"] = tabla["date"].apply(formatear_fecha_es)
    tabla["Hora"] = tabla["hora"]  # ✅ NUEVA COLUMNA
    tabla["Presentación"] = tabla["memo"]
    tabla["Valor"] = tabla["amount"].abs().apply(fmt_money)

    tabla = tabla[["Fecha", "Hora", "Presentación", "Valor"]].reset_index(drop=True)
    tabla.index = range(len(tabla), 0, -1)

    st.dataframe(tabla)