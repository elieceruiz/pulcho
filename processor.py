# processor.py

import pandas as pd
import re
from datetime import datetime


KEYWORDS_CONSUMO = [
    "CLUB COLOMBIA",
    "PILSEN",
    "COLA & POLA",
    "CAJICÁ",
    "AMPER",
    "VIVE100",
    "SPARTAN",
    "3 CORDILLERAS"
]


def to_dataframe(transactions):
    df = pd.DataFrame(transactions)

    df["amount"] = df["amount"] / 1000
    df["date"] = pd.to_datetime(df["date"])

    return df


# 🔹 FILTRO CONSUMO (MEMO)
def get_consumos(df):
    texto = df["memo"].fillna("").str.upper()
    mask = texto.apply(lambda x: any(k in x for k in KEYWORDS_CONSUMO))
    return df[mask].copy()


# 🔹 FILTRO CARVE
def get_carve(df):
    texto = df["memo"].fillna("").str.upper()
    return df[texto.str.contains("CARVE")].copy()


# 🔹 HORA DESDE MEMO
def extraer_hora(memo):
    if not isinstance(memo, str):
        return None
    
    match = re.search(r"\b(\d{2}:\d{2})\b", memo)
    if match:
        return match.group(1)
    
    return None


def agregar_hora(df):
    df = df.copy()
    df["hora"] = df["memo"].apply(extraer_hora)
    df["hora"] = df["hora"].fillna("—")
    return df


# 🔹 PRODUCTO LIMPIO
def limpiar_producto(memo):
    if not isinstance(memo, str):
        return memo
    
    limpio = re.sub(r"\b\d{2}:\d{2}\b", "", memo)
    return limpio.strip()


def agregar_producto_limpio(df):
    df = df.copy()
    df["producto"] = df["memo"].apply(limpiar_producto)
    return df


# 🔹 DATETIME REAL (CLAVE)
def construir_datetime(row):
    fecha = row["date"]

    if row["hora"] == "—":
        return fecha

    try:
        hora = datetime.strptime(row["hora"], "%H:%M").time()
        return pd.Timestamp.combine(fecha.date(), hora)
    except:
        return fecha


def agregar_datetime_real(df):
    df = df.copy()
    df["datetime"] = df.apply(construir_datetime, axis=1)
    return df


# 🔹 MÉTRICAS

def total_consumo(consumos):
    return consumos["amount"].abs().sum()


def ultimo_consumo(consumos):
    if consumos.empty:
        return None
    return consumos["datetime"].max()


def horas_sin_consumo(consumos):
    ultimo = ultimo_consumo(consumos)
    if ultimo is None:
        return 0

    ahora = pd.Timestamp.now()
    return (ahora - ultimo).total_seconds() / 3600


# 🔹 CARVE

def extraer_gramos(texto):
    if not isinstance(texto, str):
        return None
    
    match = re.search(r"(\d+)\s*g", texto.lower())
    if match:
        return float(match.group(1))
    
    return None


def resumen_carve(carve):
    carve = carve.copy()

    carve["gramos"] = carve["memo"].apply(extraer_gramos)
    carve = carve.dropna(subset=["gramos"])

    total_transacciones = len(carve)
    total_gramos = carve["gramos"].sum()
    total_valor = carve["amount"].abs().sum()

    if total_gramos == 0:
        precio_gramo = None
    else:
        precio_gramo = total_valor / total_gramos

    return {
        "transacciones": total_transacciones,
        "gramos": total_gramos,
        "precio_gramo": precio_gramo
    }