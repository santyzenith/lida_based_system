import json_repair
import pandas as pd
import warnings
from . import component_utils, llm_utils, utils
from pydantic import BaseModel
from typing import List

class FieldInfo(BaseModel):
    name: str
    description: str
    semantic_type: str

class DatasetAnnotation(BaseModel):
    dataset_description: str
    fields: List[FieldInfo]

class Summarizer():
    def __init__(self):
        self.summary = None

    def check_type(self, dtype, value):
        """
        Convierte el valor al tipo correcto para asegurar que es serializable con JSON
        """
        
        if "float" in str(dtype):
            #return float(value)
            return f"{float(value):.2f}"
            
            
        elif "int" in str(dtype):
            #return int(value)
            return f"{int(value):.2f}"
            
        else:
            return value

    def get_column_properties(self, df, n_samples=5):
        """
        Obtener las propiedades de cada columna en un DataFrame pandas
        """
        
        properties_list = []
        for column in df.columns:
            dtype = df[column].dtype
            properties = {}
            
            properties["na_count"] = (df[column].isna().sum()).item()
            properties["non_na_count"] = len(df) - properties["na_count"]
            
            if dtype in [int, float, complex]:
                properties["dtype"] = "number"
                properties["mean"] = self.check_type(dtype, df[column].mean())
                properties["std"] = self.check_type(dtype, df[column].std())
                properties["min"] = self.check_type(dtype, df[column].min())
                properties["max"] = self.check_type(dtype, df[column].max())

            elif dtype == bool:
                properties["dtype"] = "boolean"
                
            elif dtype == object:
                # Comprueba si la columna de cadena se puede convertir en una fecha/hora válida
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        pd.to_datetime(df[column], errors='raise')
                        properties["dtype"] = "date"
                except ValueError:
                    # Comprueba si la columna de strings tiene un número limitado de valores
                    #if df[column].nunique() / len(df[column]) < 0.5:
                    if df[column].nunique() < 10:
                        properties["dtype"] = "category"
                    else:
                        properties["dtype"] = "string"
                        
            elif pd.api.types.is_categorical_dtype(df[column]):
                properties["dtype"] = "category"
                
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                properties["dtype"] = "date"
                
            else:
                properties["dtype"] = str(dtype)

            # añadir min max si dtype es fecha
            if properties["dtype"] == "date":
                try:
                    properties["min"] = df[column].min()
                    properties["max"] = df[column].max()
                except TypeError:
                    cast_date_col = pd.to_datetime(df[column], errors='coerce')
                    properties["min"] = cast_date_col.min()
                    properties["max"] = cast_date_col.max()

            # Info de valores distintos
            nunique = df[column].nunique()
            properties["num_unique_values"] = nunique
            
            # Infor para ejemplos (samples)
            non_null_values = df[column][df[column].notnull()].unique()
            num_samples = min(n_samples, len(non_null_values))
            if num_samples == 0:
                samples = []
            else:
                samples = pd.Series(non_null_values).sample(num_samples, random_state=42).tolist()
            properties["samples"] = samples
            
            properties_list.append(
                {"column": column, 
                 "properties": properties}
            )

        return properties_list

    def enrich(self, base_summary, model, client):
        """
        Enriquecer el resumen de datos con descripciones
        """
        
        json_schema = DatasetAnnotation.model_json_schema()
        
        messages = [
            {"role": "system", "content": component_utils.get_summarizer_sys_prompt()},
            {"role": "user", "content": component_utils.get_summarizer_user_prompt(base_summary)}
        ]

        enriched_summary = llm_utils.get_llm_answer(client, model, messages, guided_json=json_schema)
        
        try:
            return json_repair.repair_json(enriched_summary, ensure_ascii=False, return_objects=True)
        except Exception as e:
            print(f"Error: {e}")
            raise ValueError(f"Respuesta inválida del modelo: {enriched_summary}")
            
    def summarize(self, 
                  data,
                  config, 
                  client,
                  n_samples=5, 
                  summary_method="default", 
                  encoding="utf-8"):
        """
        Resumir datos de un DataFrame de pandas o de una ubicación de archivo.
        summary_method => default, sin descripciones de llm
        summary_method => llm, con desc de llm
        summary_method => columns, sin llm, solo nombres de columnas
        """
        
        # si los datos son una ruta de archivo, se leen en un pandas DataFrame, establecer file_name al nombre del archivo
        if isinstance(data, str):
            file_name = data.split("/")[-1]
            data = utils.read_dataframe(data, encoding=encoding)
            
        data_properties = self.get_column_properties(data, n_samples)

        # construcción del resumen de una sola etapa por defecto (default)
        base_summary = {
            "file_name": file_name,
            "fields": data_properties,
        }
        

        if summary_method == "llm":
            # resumen con enriquecimiento de llm
            llm_summary = self.enrich(
                base_summary,
                config["dynamic_config"]["dynamic_model_name"],
                client
            )
            
            # Unificar y agregar la información del llm en el primer resumen
            base_summary["llm_desc"] = llm_summary['dataset_description']
            for field in base_summary['fields']:
                column_name = field['column']
                # Buscar el campo correspondiente en el segundo diccionario
                matching_field = next((item for item in llm_summary['fields'] if item['name'] == column_name), None)
                if matching_field:
                    # Agregar la descripción y el tipo semántico al primer diccionario
                    field['properties']['llm_description'] = matching_field['description']
                    field['properties']['llm_semantic_type'] = matching_field['semantic_type']
                else:
                    # Si no hay coincidencia, se pone "-"
                    field['properties']['llm_description'] = "-"
                    field['properties']['llm_semantic_type'] = "-"

        return data, base_summary, llm_summary