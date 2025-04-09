# backend.py
import yaml
import sqlite3
import re
import requests

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
def conectar_db(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    return conn, cursor

def obtener_esquema(cursor):
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()

    esquema = "Esquema de la base de datos:\n\n"
    for nombre_tabla, estructura in tablas:
        if estructura:
            esquema += f"📌 Tabla: {nombre_tabla}\n🛠 Estructura:\n{estructura}\n{'-'*60}\n"
    return esquema

# ------------------------
# Llamada a modelo (API)
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
    else:  # vLLM
        url = config["vllm_config"]["vllm_base_url"] + "/chat/completions"
        model = config["vllm_config"]["vllm_model_name"]
        headers = {
            "Content-Type": "application/json"
        }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 200
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
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

    print("Error: No se pudo extraer correctamente la consulta SQL.")
    return None

def generar_sql(orden, cursor):
    esquema = obtener_esquema(cursor)
    prompt = f"""
Eres un asistente experto en SQL. Genera una consulta SQL en UNA SOLA LÍNEA que cumpla con la siguiente instrucción: {orden}
No omitas condiciones importantes y usa el esquema proporcionado.

{esquema}

Consulta SQL:
"""
    respuesta = llamar_modelo(prompt)
    print("🔍 Consulta generada (primera vez):\n", respuesta)
    return extraer_sql(respuesta)

def regenerar_sql(orden, error, sql_anterior, cursor):
    esquema = obtener_esquema(cursor)
    prompt = f"""
Eres un asistente que corrige consultas SQL. La siguiente consulta generó un error.

Consulta original: {sql_anterior}
Error: {error}

Corrige la consulta de forma que cumpla la instrucción original. Usa UNA SOLA LÍNEA.

{esquema}

Consulta SQL corregida:
"""
    respuesta = llamar_modelo(prompt)
    print("🔄 Consulta generada (corregida):\n", respuesta)
    return extraer_sql(respuesta)

def ejecutar_orden(orden, cursor, intentos=2):
    sql_query = None
    error = ""

    for intento in range(intentos):
        print(f"\n🔁 Intento #{intento + 1} para: {orden}")

        if intento == 0:
            sql_query = generar_sql(orden, cursor)
        else:
            sql_query = regenerar_sql(orden, error, sql_query, cursor)

        if not sql_query:
            print("❌ No se pudo generar una consulta SQL válida.")
            return None

        print(f"✅ Consulta generada: {sql_query}")
        try:
            cursor.execute(sql_query)
            resultados = cursor.fetchall()
            print("🎉 Consulta ejecutada exitosamente.")
            return resultados
        except sqlite3.Error as e:
            error = str(e)
            print(f"⚠️ Error de SQL: {error}")

    print("❌ No fue posible generar una consulta válida después de varios intentos.")
    return None

def mostrar_resultados(resultados):
    if resultados:
        print("\n📄 Resultados obtenidos:")
        for fila in resultados:
            print(fila)
    else:
        print("📭 No se obtuvieron resultados.")
