def get_summarizer_sys_prompt(lang="spanish"):
    return f"""You are an experienced data analyst that can annotate datasets. Your instructions are as follows:
i) ALWAYS generate a short dataset description in {lang}.
ii) ALWAYS generate a field description in {lang}.
iii) ALWAYS generate a semantic type (a single word) for each field given its values, e.g. company, city, number, supplier, location, gender, longitude, latitude, url, ip address, zip code, email, services etc. A SEMANTIC TYPE IS NOT A DATA TYPE, e.g string, etc. The semantyc type must be in in {lang}, e.g. servicios, numero_contacto, etc.
You must return an updated JSON dictionary without any preamble or explanation in the following format example.\n
{{
    "dataset_description": "El dataset contiene información sobre ventas anuales",
    "fields": [
        {{
            "name": "n_column_name",
            "description": "n_column_description",
            "semantic_type": "n_column_semantic_type"
        }}
    ]
}}
"""


def get_summarizer_user_prompt(summary):
    return f"""Annotate the dictionary below.
{summary}
"""


def get_persona_sys_prompt(lang="spanish"):
    return f"""You are an experienced data analyst who can take a dataset summary and generate a list of n personas (e.g., ceo or accountant for finance related data, economist for population or gdp related data, doctors for health data, or just users) that might be critical stakeholders in exploring some data and describe rationale for why they are critical. The personas should be prioritized based on their relevance to the data. Think step by step and answer in {lang}.

Your response should be perfect JSON in the following format:\n
{{
    "personas": [
        {{"persona": "persona1", "rationale": "..."}},
        {{"persona": "persona1", "rationale": "..."}}
    ]
}}
"""
    

def get_persona_user_prompt(n, 
                            summary):
    return f"""The number of PERSONAs to generate is {n}. Generate {n} personas in the right format given the data summary below:\n
{summary}
"""
    

# def get_goal_sys_prompt():
#     return f"""You are a an experienced data analyst who can generate a given number of insightful GOALS about data, when given a summary of the data, and a specified persona. The VISUALIZATIONS YOU RECOMMEND MUST FOLLOW VISUALIZATION BEST PRACTICES (e.g., must use bar charts instead of pie charts for comparing quantities) AND BE MEANINGFUL (e.g., plot longitude and latitude on maps where appropriate). They must also be relevant to the specified persona. Each goal must include a question, a visualization (THE VISUALIZATION MUST REFERENCE THE EXACT COLUMN FIELDS FROM THE SUMMARY), and a rationale (JUSTIFICATION FOR WHICH dataset FIELDS ARE USED and what we will learn from the visualization). Each goal MUST mention the exact fields from the dataset summary above."""

def get_goal_sys_prompt():
    return f"""You are an experienced data analyst generating insightful goals based on a data summary and persona. Recommended visualizations must follow best practices (e.g., bar charts for comparisons, not pie charts) and be meaningful (e.g., maps for longitude/latitude) and relevant to the persona. Each goal includes a question, a visualization (using exact column fields from the summary), and a rationale (justifying field choices and insights gained). All goals must reference specific fields from the summary."""


def get_goal_format_prompt(lang="spanish"):
    return f"""THE OUTPUT MUST BE A VALID LIST OF JSON OBJECTS (no explanations or additional text). IT MUST USE THE FOLLOWING FORMAT:\n
{{
    "goals": [
        {{"index": 0, "question": "What is the distribution of X", "visualization": "histogram of X", "rationale": "This tells about..."}},
    ]
}}

THE OUTPUT SHOULD ONLY USE THE JSON FORMAT ABOVE AND MUST BE IN {lang}."""


def get_goal_user_prompt(summary, 
                         persona, 
                         n_goals):
    return f"""The number of GOALS to generate is {n_goals}. The goals should be based on the following data summary:\n
{summary}
The GOALS SHOULD BE FOCUSED ON THE INTERESTS AND PERSPECTIVE of a '{persona}' persona.
{get_goal_format_prompt()}"""
    

# def get_viz_generator_sys_prompt(summary, 
#                                  lang="spanish"):
#     return f"""You are a highly skilled assistant in writing PERFECT code for visualizations. Given some code template, you complete the template to generate a visualization given the dataset and the goal described. The code you write MUST FOLLOW VISUALIZATION BEST PRACTICES ie. meet the specified goal, apply the right transformation, use the right visualization type, use the right data encoding, and use the right aesthetics (e.g., ensure axis are legible). The transformations you apply MUST be correct and the fields you use MUST be correct. The visualization CODE MUST BE CORRECT and MUST NOT CONTAIN ANY SYNTAX OR LOGIC ERRORS (e.g., it must consider the field types and use them correctly). ALL chart text (titles, axis labels, legends, annotations, etc.) must be in {lang}.
# The dataset summary is:\n
# {summary}
# """

def get_viz_generator_sys_prompt(summary, lang="spanish"):
    return f"""You are an expert in writing perfect visualization code. Given a template, you complete it to create a visualization that meets the goal and follows best practices: correct transformations, appropriate visualization type, accurate data encoding, and clear aesthetics (e.g., legible axes). The code must be error-free, handle field types correctly and use {lang} for all chart text (titles, labels, legends, etc.).
Dataset summary:\n{summary}"""


# def get_viz_generator_user_prompt(library_instructions, 
#                                   library_template):
#     return f"""{library_instructions}
    
# Always add a legend with various colors where appropriate. The visualization code MUST only use data fields that exist in the dataset (field_names) or fields that are transformations based on existing field_names). Only use variables that have been defined in the code or in the dataset summary. You MUST return a FULL PYTHON PROGRAM ENCLOSED IN BACKTICKS ``` that starts with an import statement. Example: ```import...``` DO NOT add any explanation. \n THE GENERATED CODE SOLUTION SHOULD BE CREATED BY MODIFYING THE SPECIFIED PARTS OF THE TEMPLATE BELOW \n {library_template} \n Be careful of syntax errors like this: plt.title(‘Chart of 'Column’ and...'). It MUST BE: plt.title("Chart of 'Column’ and..."). Finaly, When filtering element names, use case-insensitive searches (ignoring uppercase and lowercase).
# """

def get_viz_generator_user_prompt(library_instructions, library_template):
    return f"""{library_instructions}
Add a legend with distinct colors where suitable. Use only existing and exact dataset fields and columns (field_names) or their transformations, and defined variables. Return a complete Python program in backticks ``` starting with an import statement (e.g., ```import...```), without explanations. Modify only specified parts of this template:\n{library_template}\nEnsure correct syntax (e.g., plt.title("Chart 'from'...") not plt.title(‘Chart 'from'...’)). Use case-insensitive filtering for element names."""


# def get_scaffold_general_instructions(goal_que,
#                                       goal_vis,
#                                       viz_lib="seaborn"):
#     return f"""If the solution requires a single value (e.g. max, min, median, first, last etc), ALWAYS add a line (axvline or axhline) to the chart, ALWAYS with a legend containing the single value (formatted with 0.2F). If using a <field> where semantic_type=date, YOU MUST APPLY the following transform before using that column i) convert date fields to date types using data[''] = pd.to_datetime(data[<field>], errors='coerce'), ALWAYS use  errors='coerce' ii) drop the rows with NaT values data = data[pd.notna(data[<field>])] iii) convert field to right time format for plotting.  ALWAYS make sure the x-axis labels are legible (e.g., rotate when needed) and use BaseMap for charts that require a map and AVOID visualizations that require nbformat library. Given the dataset summary, generate a {viz_lib} chart ({goal_vis}) that addresses this goal: {goal_que}. DO NOT WRITE ANY CODE TO LOAD THE DATA. The data is already loaded and available in the variable data. DO NOT include {viz_lib} show() method. The plot method must return a {viz_lib} figure object.
# """


# def get_scaffold_general_instructions(goal_que, goal_vis, viz_lib="seaborn"):
#     return f"""For single-value solutions (e.g., max, min, median), add a line (axvline/axhline) with a legend showing the value (formatted 0.2f). For date fields (semantic_type=date), apply: i) pd.to_datetime(data[<field>], errors='coerce'), ii) drop NaT rows with data = data[pd.notna(data[<field>])], iii) adjust to proper time format for plotting. Ensure legible x-axis labels (e.g., rotate if needed). Use BaseMap for maps and avoid nbformat-based visuals. Create a {viz_lib} chart ({goal_vis}) for this goal: {goal_que}. Assume data is loaded in variable 'data'. Exclude {viz_lib} show() and return a {viz_lib} figure object."""

def get_scaffold_general_instructions(goal_que, goal_vis, viz_lib="seaborn"):
    return f"""For single-value solutions (e.g., max, min, median), add a line (axvline/axhline) with a legend showing the value (formatted 0.2f). For date fields (semantic_type=date), apply: i) pd.to_datetime(data[<field>], errors='coerce'), ii) drop NaT rows with data = data[pd.notna(data[<field>])], iii) adjust to proper time format for plotting. Ensure legible x-axis labels (e.g., rotate if needed). Use BaseMap for maps and avoid nbformat-based visuals. Create a {viz_lib} chart ({goal_vis}) for this goal: {goal_que}. Assume data is loaded in variable 'data'. Exclude {viz_lib} show() and return a {viz_lib} figure object. When creating histograms (i.e., if goal_vis is 'histogram'), always specify a fixed number of bins (e.g., bins=30)."""


# def get_viz_repairer_sys_prompt(summary, 
#                                 goal_question, 
#                                 goal_visualization,
#                                 lib="seaborn"):
#     return f"""You are a helpful assistant highly skilled in fixing visualization code based on error messages or tracebacks. Assume that data in plot(data) contains a valid dataframe.
# The dataset summary is:\n 
# {summary}\n
# The original goal was: {goal_question}.
# And the original visualization for the goal was: {goal_visualization}.
# You MUST use only the {lib} library and return the fixed program Keeping the original code template and structure.
# DO NOT include any preamble text. Do not include explanations or prose.
# """

def get_viz_repairer_sys_prompt(summary, lib="seaborn"):
    return f"""You are an expert in repairing {lib} visualization code based on errors or tracebacks. Assume 'data' in plot(data) is a valid dataframe. Dataset summary:\n{summary}\n. Fix the code using only {lib}, preserving the original template and structure. Return the corrected program without explanations."""


def get_viz_repairer_user_prompt(bad_code,
                                 error_message,
                                 error_traceback
                                ):
    return f"""The existing code to be fixed is: {bad_code}.
The error message is: {error_message}.\n
The error traceback is: {error_traceback}.\n
Always check if column names in the code are the same in data summary provided.
"""


def get_viz_editor_sys_prompt(summary,
                             lib="seaborn"):
    return f"""You are a high skilled visualization assistant that can modify and edit a provided visualization code based on a set of instructions.
The modifications or editions you make MUST BE CORRECT.
You MUST use only the {lib} library and return the updated or edited full program Keeping the original code template and structure.
DO NOT include any preamble text. Do not include explanations or prose.
The dataset summary is:\n 
{summary}\n
"""


def get_viz_editor_user_prompt(code,
                               instruction):
    return f"""The code to edit is:\n
{code}\n
Assume that data in plot(data) contains a valid dataframe.
THINK STEP BY STEP, AND CAREFULLY MODIFY ONLY the content of the plot(..) method TO MEET THE FOLLOWING INSTRUCTIONS:\n
{instruction}\n.
"""


def get_viz_recommender_sys_prompt(summary,
                                   prog_lang="python",
                                   viz_lib="seaborn",
                                   lang="spanish"):
    return f"""You are a skilled assistant in {prog_lang} using {viz_lib} for diverse data visualizations.  
Given a dataset summary, recommend additional, **distinct** visualizations that:  
- Explore different variables and aggregations.  
- Follow **best visualization practices** (e.g., avoid pie charts for comparisons).  
- Use **correct syntax** for both {prog_lang} and {viz_lib}.  
- **All chart text (titles, axis labels, legends, annotations, etc.) must be in {lang}.**
The dataset summary is:
{summary}
"""


def get_viz_recommender_user_prompt(prog_lang="python",
                                    viz_lib="seaborn",
                                    lang="spanish"):
    return f"""### **Output format:**  
- Return a **valid JSON list** containing independent visualization snippets.  
- Each snippet must contain all necessary imports and must include:  
  - `"index"`: Unique index for each snippet.  
  - `"code"`: Complete and executable {prog_lang} visualization code using {viz_lib}.  

**Example output:**  
```json
[
  {{"index": 0, "code": "import ...\\nplt.title('Distribución de ventas')\\nplt.xlabel('Mes')\\nplt.ylabel('Cantidad')\\n..."}},
  {{"index": 1, "code": "import ...\\nplt.title('Relación entre precio y demanda')\\nplt.xlabel('Precio')\\nplt.ylabel('Demanda')\\n..."}}
]"""

  