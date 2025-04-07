from . import component_utils, llm_utils, utils

class VizEditor():
    """Generate visualizations from prompt"""

    def __init__(self):
        pass

    def generate(
        self, 
        code, 
        summary,
        instruction,
        config, 
        client, 
        library="seaborn"
    ):
        """Edit a code spec based on instructions"""
        
        messages = [
            {"role": "system", "content": component_utils.get_viz_editor_sys_prompt(summary,
                                                                                    lib=library)},
            
            {"role": "user", "content": component_utils.get_viz_editor_user_prompt(code, 
                                                                                   instruction)}
        ]
        
        llm_edited_code = llm_utils.get_llm_answer(client, 
                                                   config["dynamic_config"]["dynamic_model_name"], 
                                                   messages, 
                                                   #guided_json=json_schema
                                                  )

        return llm_edited_code
        