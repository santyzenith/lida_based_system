#from dataclasses import asdict
#from goal import Goal
from . import component_utils

class ChartScaffold():
    """
    Return code scaffold for charts in multiple visualization libraries
    """

    def __init__(self):
        pass

    def get_template(self, 
                     goal_question, 
                     goal_visualization, 
                     viz_library="seaborn"):

        print("scafold_ques", goal_question)
        print("scafold_vis", goal_visualization)
        print("scafold_lib", viz_library)

        if viz_library == "seaborn":
            instructions = component_utils.get_scaffold_general_instructions(goal_question,
                                                                             goal_visualization,
                                                                             viz_lib=viz_library
                                                                             )

            template = f"""
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
<imports>

def plot(data: pd.DataFrame):

    <stub> # only modify this section
    plt.title('{goal_question}', wrap=True)
    return plt;

chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line."""


        elif library == "plotly":
            instructions = component_utils.get_scaffold_general_instructions(goal_question,
                                                                             goal_visualization,
                                                                             viz_lib="seaborn"
                                                                             )
            
            template = f"""
import plotly.express as px
<imports>
def plot(data: pd.DataFrame):
    fig = <stub> # only modify this section
    fig.update_layout(title='{goal_question}')
    return chart
chart = plot(data) # variable data already contains the data to be plotted and should not be loaded again.  Always include this line. No additional code beyond this line..
"""

        else:
            raise ValueError(
                "Unsupported library. Choose from 'seaborn', 'plotly'."
            )

        return template, instructions

            

#         general_instructions = f"If the solution requires a single value (e.g. max, min, median, first, last etc), ALWAYS add a line (axvline or axhline) to the chart, ALWAYS with a legend containing the single value (formatted with 0.2F). If using a <field> where semantic_type=date, YOU MUST APPLY the following transform before using that column i) convert date fields to date types using data[''] = pd.to_datetime(data[<field>], errors='coerce'), ALWAYS use  errors='coerce' ii) drop the rows with NaT values data = data[pd.notna(data[<field>])] iii) convert field to right time format for plotting.  ALWAYS make sure the x-axis labels are legible (e.g., rotate when needed) and use BaseMap for charts that require a map. Given the dataset summary, generate a {library} chart ({goal.visualization}) that addresses this goal: {goal.question}. DO NOT WRITE ANY CODE TO LOAD THE DATA. The data is already loaded and available in the variable data."

#         matplotlib_instructions = f" {general_instructions} DO NOT include plt.show(). The plot method must return a matplotlib object (plt). Think step by step. \n"

#         if library == "matplotlib":
#             instructions = {
#                 "role": "assistant",
#                 "content": f"  {matplotlib_instructions}. Use BaseMap for charts that require a map. "}
#             template = \
#                 f"""
# import matplotlib.pyplot as plt
# import pandas as pd
# <imports>
# # plan -
# def plot(data: pd.DataFrame):
#     <stub> # only modify this section
#     plt.title('{goal.question}', wrap=True)
#     return plt;

# chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line."""
#         elif library == "seaborn":
#             instructions = {
#                 "role": "assistant",
#                 "content": f"{matplotlib_instructions}. Use BaseMap for charts that require a map. "}

#             template = \
#                 f"""
# import seaborn as sns
# import pandas as pd
# import matplotlib.pyplot as plt
# <imports>

# def plot(data: pd.DataFrame):

#     <stub> # only modify this section
#     plt.title('{goal.question}', wrap=True)
#     return plt;

# chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line."""

#         elif library == "ggplot":
#             instructions = {
#                 "role": "assistant",
#                 "content": f"{general_instructions}. The plot method must return a ggplot object (chart)`. Think step by step.p. \n",
#             }

#             template = \
#                 f"""
# import plotnine as p9
# <imports>
# def plot(data: pd.DataFrame):
#     chart = <stub>

#     return chart;

# chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line.. """

#         elif library == "altair":
#             instructions = {
#                 "role": "system",
#                 "content": f"{general_instructions}. Always add a type that is BASED on semantic_type to each field such as :Q, :O, :N, :T, :G. Use :T if semantic_type is year or date. The plot method must return an altair object (chart)`. Think step by step. \n",
#             }
#             template = \
#                 """
# import altair as alt
# <imports>
# def plot(data: pd.DataFrame):
#     <stub> # only modify this section
#     return chart
# chart = plot(data) # data already contains the data to be plotted.  Always include this line. No additional code beyond this line..
# """

#         elif library == "plotly":
#             instructions = {
#                 "role": "system",
#                 "content": f"{general_instructions} If calculating metrics such as mean, median, mode, etc. ALWAYS use the option 'numeric_only=True' when applicable and available, AVOID visualizations that require nbformat library. DO NOT inlcude fig.show(). The plot method must return an plotly figure object (fig)`. Think step by step. \n.",
#             }
#             template = \
#                 """
# import plotly.express as px
# <imports>
# def plot(data: pd.DataFrame):
#     fig = <stub> # only modify this section

#     return chart
# chart = plot(data) # variable data already contains the data to be plotted and should not be loaded again.  Always include this line. No additional code beyond this line..
# """

#         else:
#             raise ValueError(
#                 "Unsupported library. Choose from 'matplotlib', 'seaborn', 'plotly', 'bokeh', 'ggplot', 'altair'."
#             )

#         return template, instructions
