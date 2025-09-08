from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import re

# Normalización de nombres de columnas posibles
COLUMN_ALIASES = {
    "ApellidoPaterno": ["apellido paterno", "apellidopaterno", "ap paterno", "ap_paterno", "apellido_paterno"],
    "ApellidoMaterno": ["apellido materno", "apellidomaterno", "ap materno", "ap_materno", "apellido_materno"],
    "Nombres": ["nombres", "nombre", "name", "nombres y apellidos"],
    "DNI": ["dni", "documento", "documento identidad", "num doc", "numero documento", "n.º documento"],
    "Correo": ["correo", "email", "e-mail", "mail", "correo electronico", "correo electrónico"],
}


def _normalize(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    s = re.sub(r"\s+", " ", s)
    return s


def _map_columns(columns: list) -> dict:
    mapping = {}
    for col in columns:
        norm = _normalize(str(col))
        for target, aliases in COLUMN_ALIASES.items():
            if norm == _normalize(target) or norm in [_normalize(a) for a in aliases]:
                mapping[col] = target
                break
    return mapping


def load_contacts(path: Path, sheet_name: Optional[str] = None) -> List[Dict]:
    """Carga contactos desde Excel o CSV, normaliza columnas y filtra registros válidos.

    Requiere al menos columnas mapeadas a: Nombres, ApellidoPaterno, ApellidoMaterno, DNI, Correo.
    """
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path, sheet_name=sheet_name)
    elif path.suffix.lower() in {".csv"}:
        try:
            df = pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin1")
    else:
        raise ValueError("Formato no soportado. Usa .xlsx o .csv")

    if df.empty:
        return []

    # Mapear columnas a nombres estándar
    mapping = _map_columns(list(df.columns))
    df = df.rename(columns=mapping)

    required = ["Nombres", "ApellidoPaterno", "ApellidoMaterno", "DNI", "Correo"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(missing)}")

    # Limpiar nulos y espacios
    for c in required:
        df[c] = df[c].astype(str).fillna("").str.strip()

    # Filtrar correos vacíos
    df = df[df["Correo"].str.contains("@")]

    # Convertir a registros
    rows: List[Dict] = df.to_dict(orient="records")
    return rows
