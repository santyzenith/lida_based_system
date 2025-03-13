import pandas as pd
import yaml
import re

def load_config(config_path="config/config.yaml"):
    """
    Cargar configuración desde un archivo yaml
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config

def read_dataframe(file_location, encoding='utf-8'):
    """
    Lee un dataframe de una ubicación de archivo dada y limpia los nombres de sus columnas.
    :param file_location: La ruta al fichero que contiene los datos.
    :param encoding: Codificación a utilizar para la lectura del fichero.
    :return: Un DataFrame limpio.
    """
    
    file_extension = file_location.split('.')[-1]

    read_funcs = {
        'json': lambda: pd.read_json(file_location, orient='records', encoding=encoding),
        'csv': lambda: pd.read_csv(file_location, encoding=encoding),
        'xls': lambda: pd.read_excel(file_location, encoding=encoding),
        'xlsx': lambda: pd.read_excel(file_location, encoding=encoding),
        'parquet': pd.read_parquet,
        'feather': pd.read_feather,
        'tsv': lambda: pd.read_csv(file_location, sep="\t", encoding=encoding)
    }

    if file_extension not in read_funcs:
        raise ValueError('Unsupported file type')

    try:
        df = read_funcs[file_extension]()
    except Exception as e:
        logger.error(f"Error al leer el archivo: {file_location}. Error: {e}")
        raise
        
    # Limpiar nombres de columna
    cleaned_df = clean_column_names(df)

    if cleaned_df.columns.tolist() != df.columns.tolist():
        write_funcs = {
            'csv': lambda: cleaned_df.to_csv(file_location, index=False, encoding=encoding),
            'xls': lambda: cleaned_df.to_excel(file_location, index=False),
            'xlsx': lambda: cleaned_df.to_excel(file_location, index=False),
            'parquet': lambda: cleaned_df.to_parquet(file_location, index=False),
            'feather': lambda: cleaned_df.to_feather(file_location, index=False),
            'json': lambda: cleaned_df.to_json(file_location, orient='records', index=False, default_handler=str),
            'tsv': lambda: cleaned_df.to_csv(file_location, index=False, sep='\t', encoding=encoding)
        }

        if file_extension not in write_funcs:
            raise ValueError('Unsupported file type')

        try:
            write_funcs[file_extension]()
        except Exception as e:
            logger.error(f"Error al escribir el archivo: {file_location}. Error: {e}")
            raise

    return cleaned_df

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia todos los nombres de columna del DataFrame dado.
    param df: El DataFrame con nombres de columnas posiblemente sucios.
    :return: Una copia del DataFrame con los nombres de las columnas limpios.
    """
    
    cleaned_df = df.copy()
    cleaned_df.columns = [clean_column_name(col) for col in cleaned_df.columns]
    return cleaned_df

def clean_column_name(col_name: str) -> str:
    """
    Limpia el nombre de una columna sustituyendo los caracteres especiales y los espacios por guiones bajos.
    :param nombre_columna: El nombre de la columna a limpiar.
    :return: Una cadena limpiada válida como nombre de columna.
    """
    
    return re.sub(r'[^0-9a-zA-Z_]', '_', col_name).strip()


def summarize_properties_to_df(properties_list):
    """
    Convierte la lista de propiedades de columnas en un DataFrame.

    Parámetros:
        properties_list (list): Lista de diccionarios con propiedades de cada columna.

    Retorna:
        pd.DataFrame: DataFrame con la información estructurada.
    """
    rows = []
    
    for item in properties_list:
        column_name = item["column"]
        properties = item["properties"]
        
        # Extraer valores, asegurando que existan en properties
        row = {
            "column": column_name,
            "dtype": properties.get("dtype", ""),
            "mean": properties.get("mean", None),
            "std": properties.get("std", None),
            "min": properties.get("min", None),
            "max": properties.get("max", None),
            "samples": ", ".join(map(str, properties.get("samples", []))),  # Convertir lista a string
            "num_unique_values": properties.get("num_unique_values", None),
            "na_count": properties.get("na_count", None),
            "non_na_count": properties.get("non_na_count", None),
            "llm_description": properties.get("llm_description", None),
            "llm_semantic_type": properties.get("llm_semantic_type", None),
        }
        
        rows.append(row)
    
    return pd.DataFrame(rows)
