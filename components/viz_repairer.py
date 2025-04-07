import copy
from typing import Dict, List, Union
from . import component_utils, llm_utils, utils

class VizRepairer():
    """Fix visualization code based on feedback"""

    def __init__(self):
        pass
        
    def generate(
        self, 
        summary,
        code, 
        error_msg,
        error_trace,
        config,
        client,
        library="seaborn"):
        """Fix a code spec based on error message"""

        #goals_with_bad_code = copy.deepcopy(in_goals_with_bad_code)
        #for goal in goals_with_bad_code["goals"]:

        messages = [
            {"role": "system", "content": component_utils.get_viz_repairer_sys_prompt(summary, 
                                                                                      lib="seaborn")},

            {"role": "user", "content": component_utils.get_viz_repairer_user_prompt(code, 
                                                                                     error_msg,
                                                                                     error_trace
                                                                                    )}
        ]
        
        llm_repaired_code = llm_utils.get_llm_answer(client, 
                                                     config["dynamic_config"]["dynamic_model_name"], 
                                                     messages, 
                                                     #guided_json=json_schema
                                                    )

            #goal["code"] = llm_repaired_code

        return llm_repaired_code