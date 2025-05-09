# backend_duckdb.py
import yaml
import re
import duckdb
import requests
from pathlib import Path

# ------------------------
# Cargar configuración
# ------------------------
def cargar_config(path="config/config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

config = cargar_config()

# ------------------------
# Conexión base de datos
# ------------------------
def conectar_db(path=":memory:"):
    conn = duckdb.connect(database=path)
    return conn

def obtener_esquema(conn):
    tablas = conn.sql("SHOW TABLES").fetchall()
    esquema = "Esquema de la base de datos:\n\n"
    for (tabla,) in tablas:
        ddl = conn.sql(f"DESCRIBE {tabla}").df()
        estructura = "\n".join([f"{col} {dtype}" for col, dtype, *_ in ddl.values])
        esquema += f"📌 Tabla: {tabla}\n🛠 Estructura:\n{estructura}\n{'-'*60}\n"
    return esquema

# ------------------------
# Cargar archivo como tabla (DuckDB lo hace directo)
# ------------------------


def cargar_archivo(path_archivo, conn):
    if not path_archivo:
        raise ValueError("Se esperaba una ruta de archivo válida, pero se recibió None.")

    nombre_tabla = Path(path_archivo).stem
    path_seguro = Path(path_archivo).as_posix()

    if path_seguro.endswith(".csv"):
        conn.sql(f"CREATE OR REPLACE TABLE {nombre_tabla} AS SELECT * FROM read_csv_auto('{path_seguro}')")
    elif path_seguro.endswith(".xlsx"):
        conn.sql(f"CREATE OR REPLACE TABLE {nombre_tabla} AS SELECT * FROM read_xlsx('{path_seguro}')")
    else:
        raise ValueError("Formato de archivo no soportado")


# ------------------------
# Llamada a modelo
# ------------------------
def llamar_modelo(prompt):
    provider = ""
    if config["openrouter_config"]["openrouter_model_name"]:
        provider = "openrouter"
    elif config["vllm_config"]["vllm_model_name"]:
        provider = "vllm"
    else:
        raise ValueError("⚠️ No se ha configurado ningún modelo en config.yaml.")

    if provider == "openrouter":
        url = config["openrouter_config"]["openrouter_base_url"] + "/chat/completions"
        model = config["openrouter_config"]["openrouter_model_name"]
        headers = {
            "Authorization": f"Bearer {config['api_keys']['openrouter']}",
            "Content-Type": "application/json"
        }
    else:
        url = config["vllm_config"]["vllm_base_url"] + "/chat/completions"
        model = config["vllm_config"]["vllm_model_name"]
        headers = {"Content-Type": "application/json"}

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 200
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"❌ Error {response.status_code}: {response.text}")

# ------------------------
# Utilidades SQL
# ------------------------
def extraer_sql(texto):
    match = re.search(r"\b(SELECT|WITH|INSERT|UPDATE|DELETE)\b.+?(;|$)", texto, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(0).strip()
    for linea in texto.splitlines():
        if ";" in linea:
            return linea.strip()
    return None

def generar_sql(orden, conn):
    print("Inicio de generación SQL: ")
    esquema = obtener_esquema(conn)
    prompt = f"""
Eres un asistente experto en SQL. Genera una consulta SQL en UNA SOLA LÍNEA que cumpla con la siguiente instrucción: {orden}
No omitas condiciones importantes y usa el esquema proporcionado.

{esquema}

Consulta SQL:
"""
    respuesta = llamar_modelo(prompt)
    print("Consulta generada (primera vez):\n", respuesta)
    return extraer_sql(respuesta)

def regenerar_sql(orden, error, sql_anterior, conn):
    esquema = obtener_esquema(conn)
    prompt = f"""
Eres un asistente que corrige consultas SQL. La siguiente consulta generó un error.

Consulta original: {sql_anterior}
Error: {error}

Corrige la consulta de forma que cumpla la instrucción original. Usa UNA SOLA LÍNEA.

{esquema}

Consulta SQL corregida:
"""
    respuesta = llamar_modelo(prompt)
    print("Consulta generada (corregida):\n", respuesta)
    return extraer_sql(respuesta)

def ejecutar_orden(orden, conn, intentos=2):
    print("Inicio de ejecución de orden: ")
    sql_query = None
    error = ""

    for intento in range(intentos):
        print(f"\nIntento #{intento + 1} para: {orden}")
        if intento == 0:
            sql_query = generar_sql(orden, conn)
        else:
            sql_query = regenerar_sql(orden, error, sql_query, conn)

        if not sql_query:
            print("No se pudo generar una consulta SQL válida.")
            return None

        print(f"✅ Consulta generada: {sql_query}")
        try:
            resultado = conn.sql(sql_query).fetchall()
            print("Consulta ejecutada exitosamente.")
            return resultado
        except Exception as e:
            error = str(e)
            print(f"Error de SQL: {error}")

    print("❌ No fue posible generar una consulta válida después de varios intentos.")
    return None

def mostrar_resultados(resultados):
    if resultados:
        print("\nResultados obtenidos:")
        for fila in resultados:
            print(fila)
    else:
        print("No se obtuvieron resultados.")
