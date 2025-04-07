import json_repair
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
from . import component_utils, llm_utils, utils


class Persona(BaseModel):
    persona: str
    rationale: str

class DataPersona(BaseModel):
    personas: List[Persona]

class PersonaExplorer():
    """Generate personas given a summary of data"""

    def __init__(self):
        pass

    def generate(self, 
                 summary, 
                 config,
                 client, 
                 n=3):
        """Generate personas given a summary of data"""
        
        json_schema = DataPersona.model_json_schema()

        messages = [
            {"role": "system", "content": component_utils.get_persona_sys_prompt()},
            {"role": "user", "content": component_utils.get_persona_user_prompt(n, summary)}
        ]
        
        llm_personas = llm_utils.get_llm_answer(client, 
                                                config["dynamic_config"]["dynamic_model_name"], 
                                                messages, 
                                                guided_json=json_schema)

        try:
            return json_repair.repair_json(llm_personas, ensure_ascii=False, return_objects=True)
        except Exception as e:
            print(f"Error: {e}")
            raise ValueError("The model did not return a valid JSON object while attempting generate personas.  Consider using a larger model or a model with higher max token length.")
