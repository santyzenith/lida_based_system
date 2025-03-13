import json
from pydantic import BaseModel
from typing import List
from . import component_utils, llm_utils, utils

class Goal(BaseModel):
    index: int
    question: str
    visualization: str  # Debe referenciar las columnas exactas del dataset
    rationale: str  # Justificación de por qué se elige esta visualización

class DataGoals(BaseModel):
    goals: List[Goal]


class GoalExplorer():
    
    def __init__(self):
        pass

    def generate(self, 
                 summary, 
                 config, 
                 client, 
                 persona="A highly skilled data analyst who can come up with complex, insightful goals about data", 
                 n=3):
        """
        Generar objetivos a partir de un resumen de datos
        """

        json_schema = DataGoals.model_json_schema()

        messages = [
            {"role": "system", "content": component_utils.get_goal_sys_prompt()},
            {"role": "user", "content": component_utils.get_goal_user_prompt(summary, persona, n)}
        ]
        
        llm_goals = llm_utils.get_llm_answer(client, 
                                             config["dynamic_config"]["dynamic_model_name"], 
                                             messages, 
                                             guided_json=json_schema)
        
        try:
            return json.loads(llm_goals)
        except json.decoder.JSONDecodeError:
            print(f"Error al decodificar JSON: {llm_goals}")
            raise ValueError(f"Respuesta inválida del modelo: {llm_goals}")
            