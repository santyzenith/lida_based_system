import copy
from .scaffold import ChartScaffold
from . import component_utils, llm_utils, utils


class VizGenerator():
    """Generate visualizations from prompt"""

    def __init__(self):
        pass

    def generate(self, 
                 summary, 
                 in_goals, 
                 config, 
                 client, 
                 library="seaborn"):
        """Generate visualization code given a summary and a goal"""

        goals = copy.deepcopy(in_goals)
        for goal in goals["goals"]:
            #print(goal["question"])
            #print(goal["visualization"])
            chartsc = ChartScaffold()
            library_template, library_instructions = chartsc.get_template(goal["question"],
                                                                          goal["visualization"],
                                                                          library)

            messages = [
                {"role": "system", "content": component_utils.get_viz_generator_sys_prompt(summary, lang="spanish")},
                {"role": "user", "content": component_utils.get_viz_generator_user_prompt(library_instructions, library_template)}
            ]
            
            llm_code_string = llm_utils.get_llm_answer(client, 
                                                       config["dynamic_config"]["dynamic_model_name"], 
                                                       messages, 
                                                       #guided_json=json_schema
                                                      )
            
            goal["code"] = llm_code_string

        return goals, messages

    # def generate_from_prompt(self, 
    #                          summary, 
    #                          in_goals, 
    #                          config, 
    #                          client, 
    #                          library="seaborn"):
        
    #     """Generate visualization code given a summary and a goal"""

    #     goals = copy.deepcopy(in_goals)
    #     for goal in goals["goals"]:
    #         library_template, library_instructions = ChartScaffold.get_template(goal["question"],
    #                                                                             goal["visualization"],
    #                                                                             library)

    #         messages = [
    #             {"role": "system", "content": component_utils.get_viz_generator_sys_prompt(summary, lang="spanish")},
    #             {"role": "user", "content": component_utils.get_viz_generator_user_prompt(library_instructions, library_template)}
    #         ]
            
    #         llm_code_string = llm_utils.get_llm_answer(client, 
    #                                                    config["dynamic_config"]["dynamic_model_name"], 
    #                                                    messages, 
    #                                                    #guided_json=json_schema
    #                                                   )
            
    #         goal["code"] = llm_code_string

    #     return goals    