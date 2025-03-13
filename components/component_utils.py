def get_summarizer_sys_prompt(lang="spanish"):
    return f"""You are an experienced data analyst that can annotate datasets in {lang}. Your instructions are as follows:
i) ALWAYS generate a short dataset_description.
ii) ALWAYS generate a field description.
iii) ALWAYS generate a semantic_type (a single word) for each field given its values e.g. company, city, number, supplier, location, gender, longitude, latitude, url, ip address, zip code, email, etc.
You must return an updated JSON dictionary without any preamble or explanation. Remember answer in {lang}."""

def get_summarizer_user_prompt(summary):
    return f"""Annotate the dictionary below.
{summary}"""
    

def get_goal_sys_prompt(lang="spanish"):
    return f"""You are a an experienced data analyst who can generate a given number of insightful GOALS about data in {lang}, when given a summary of the data, and a specified persona. The VISUALIZATIONS YOU RECOMMEND MUST FOLLOW VISUALIZATION BEST PRACTICES (e.g., must use bar charts instead of pie charts for comparing quantities) AND BE MEANINGFUL (e.g., plot longitude and latitude on maps where appropriate). They must also be relevant to the specified persona. Each goal must include a question, a visualization (THE VISUALIZATION MUST REFERENCE THE EXACT COLUMN FIELDS FROM THE SUMMARY), and a rationale (JUSTIFICATION FOR WHICH dataset FIELDS ARE USED and what we will learn from the visualization). Each goal MUST mention the exact fields from the dataset summary above."""


def get_goal_format_prompt(lang="spanish"):
    return f"""THE OUTPUT MUST BE A VALID LIST OF JSON OBJECTS (no explanations or additional text). IT MUST USE THE FOLLOWING FORMAT:
```[
{{ "index": 0,  "question": "What is the distribution of X", "visualization": "histogram of X", "rationale": "This tells about..."}} ..
]
```
THE OUTPUT SHOULD ONLY USE THE JSON FORMAT ABOVE AND MUST BE IN {lang}."""


def get_goal_user_prompt(data_summary, persona, n_goals):
    return f"""The number of GOALS to generate is {n_goals}. The goals should be based on the following data summary:
{data_summary}
The GOALS SHOULD BE FOCUSED ON THE INTERESTS AND PERSPECTIVE of a '{persona}' persona.
{get_goal_format_prompt()}"""


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

        EACH CODE SNIPPET MUST BE A FULL PROGRAM (IT MUST IMPORT ALL THE LIBRARIES THAT ARE USED AND MUST CONTAIN plot(data) method). IT MUST FOLLOW THE STRUCTURE BELOW AND ONLY MODIFY THE INDICATED SECTIONS. \n\n {library_template} \n\n.

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

                   