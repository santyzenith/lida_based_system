import streamlit as st
import os
import pandas as pd
from components import component_utils, llm_utils, utils
from components.summarizer import Summarizer
from components.persona import PersonaExplorer
from components.goal import GoalExplorer
from components.viz_generator import VizGenerator
from components.executor import ChartExecutor
from components.viz_repairer import VizRepairer
from components.viz_editor import VizEditor
from PIL import Image
import io
import base64

# Configuración inicial
st.set_page_config(
    page_title="Generación automática de visualizaciones utilizando LLMs",
    page_icon="📊",
    layout="wide"
)

import streamlit as st
import base64

# Función para convertir imagen a base64
def get_base64_image(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Ruta de tu logo
logo_path = "images/logo.png"
logo_base64 = get_base64_image(logo_path)

# Contenedor con fondo azul y logo
with st.container():
    st.markdown(
        f'<div style="background-color: #0070B4; padding: 10px; border-radius: 5px; text-align: center;">'
        f'<img src="data:image/png;base64,{logo_base64}" width="200">'
        f'</div>',
        unsafe_allow_html=True
    )

st.write("# Generación automática de visualizaciones utilizando LLMs 📊")
st.sidebar.write("# Configuración")

# Cargar configuración y cliente LLM
my_config = utils.load_config()

st.markdown(
    """
Este servicio de Inteligencia Artificial transforma conjuntos de datos en visualizaciones avanzadas mediante Modelos de Lenguaje a Gran Escala (LLMs) y Procesamiento de Lenguaje Natural (NLP). Analiza información compleja con precisión experta y genera interpretaciones significativas, claras y accionables.
    """
)

# Inicializar session_state para todas las variables clave
if "llm_summ" not in st.session_state:
    st.session_state.llm_summ = None
if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = None
if "data" not in st.session_state:
    st.session_state.data = None
if "dataset_selectbox_enabled" not in st.session_state:
    st.session_state.dataset_selectbox_enabled = False # True
if "dataset_selectbox_index" not in st.session_state:
    st.session_state.dataset_selectbox_index = 0
if "selected_goal" not in st.session_state:
    st.session_state.selected_goal = None
if "llm_goals" not in st.session_state:
    st.session_state.llm_goals = None
if "llm_personas" not in st.session_state:
    st.session_state.llm_personas = None
if "user_persona_input" not in st.session_state:
    st.session_state.user_persona_input = ""
if "user_goal_input" not in st.session_state:
    st.session_state.user_goal_input = ""
if "charts" not in st.session_state:
    st.session_state.charts = None
if "goals_with_code" not in st.session_state:
    st.session_state.goals_with_code = None
if "edit_prompt" not in st.session_state:
    st.session_state.edit_prompt = None
if "repair_code" not in st.session_state:
    st.session_state.repair_code = None
if "show_edit_input" not in st.session_state:
    st.session_state.show_edit_input = False
if "do_repair" not in st.session_state:
    st.session_state.do_repair = False

# Configuración del sidebar
if my_config:
    with st.sidebar.expander("## Configuración del LLM", expanded=False):
        st.write("### Modelo de Generación de Texto")
        vllm_model = "vLLM-" + my_config["vllm_config"]["vllm_model_name"]
        openrouter_model = "openRouter-" + my_config["openrouter_config"]["openrouter_model_name"]
        models = ["vllm", "openrouter"]
        selected_model = st.selectbox(
            '¿Qué LLM vas a utilizar?',
            options=models,
            index=1,
            placeholder="Selecciona un LLM..."
        )

        my_config, my_client = llm_utils.load_llm_client(my_config, provider=selected_model)

        st.write("### Temperatura del LLM")
        temperature = st.slider(
            "Incrementar para respuestas más creativas",
            min_value=0.0,
            max_value=1.0,
            value=1.0
        )
        
        st.write("### Librería Visualización")
        visualization_libraries = ["seaborn"]
        selected_library = st.selectbox(
            'Selecciona una librería de visualización',
            options=visualization_libraries,
            index=0
        )

    # Selección de dataset
    st.sidebar.write("## Resumen de Datos")
    st.sidebar.write("### Selecciona un Dataset")
    datasets = [
        {"label": "Selecciona un Dataset", "url": None, "encoding": None},
        {"label": "Economía Ecuador 2023", "url": "data/new_datos_financieros_empresas_ecuador_2023.csv", "encoding": "utf-8"},
        {"label": "IQR Economía Ecuador 2023", "url": "data/iqr_datos_economicos_empresas_ecuador_2023.csv", "encoding": "utf-8"},
        {"label": "Hoteles", "url": "data/Worlds Best 50 Hotels.csv", "encoding": "latin-1"},
        {"label": "Cars", "url": "https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv", "encoding": "utf-8"},
        {"label": "Weather", "url": "https://raw.githubusercontent.com/uwdata/draco/master/data/weather.json", "encoding": "utf-8"},
    ]

    selected_dataset_label = st.sidebar.selectbox(
        'Escoge un dataset previamente cargado',
        options=[dataset["label"] for dataset in datasets],
        index=st.session_state.dataset_selectbox_index,
        disabled=st.session_state.dataset_selectbox_enabled,
    )

    upload_own_data = st.sidebar.checkbox("Sube tus datos", value=False, key="dataset_selectbox_enabled")
    selected_dataset = None
    selected_dataset_enc = None

    if upload_own_data:
        uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])
        if uploaded_file is not None:
            uploaded_file_path = os.path.join("data", uploaded_file.name)
            data = pd.read_csv(uploaded_file, encoding="utf-8")
            data.to_csv(uploaded_file_path, index=False)
            selected_dataset = uploaded_file_path
            datasets.append({"label": uploaded_file.name, "url": uploaded_file_path, "encoding": "utf-8"})
    else:
        selected_dataset = datasets[[dataset["label"] for dataset in datasets].index(selected_dataset_label)]["url"]
        selected_dataset_enc = datasets[[dataset["label"] for dataset in datasets].index(selected_dataset_label)]["encoding"]

    if not selected_dataset:
        #st.info('Asegúrese de seleccionar y verificar el objetivo de visualización', icon="ℹ️")
        st.info("Para continuar, selecciona o sube un dataset en la barra lateral izquierda.", icon="ℹ️")

    # Selección del método de resumen
    st.sidebar.write("### Selecciona un método de resumen")
    summarization_methods = [
        {"label": "llm", "description": "Utiliza un LLM para generar un resumen..."},
        {"label": "default", "description": "Utiliza las estadísticas de las columnas..."},
        {"label": "columns", "description": "Utiliza los nombres de las columnas..."}
    ]
    selected_method_label = st.sidebar.selectbox(
        'Selecciona un método',
        options=[method["label"] for method in summarization_methods],
        index=0
    )
    selected_method = summarization_methods[[method["label"] for method in summarization_methods].index(selected_method_label)]["label"]
    selected_summary_method_description = summarization_methods[[method["label"] for method in summarization_methods].index(selected_method_label)]["description"]
    st.sidebar.markdown(f"<p>{selected_summary_method_description}</p>", unsafe_allow_html=True)

    gen_df_summ_button = st.sidebar.button("Generar Resumen")

    # Generar resumen
    if gen_df_summ_button and my_config and selected_dataset and selected_method and selected_model:
        summ = Summarizer()
        with st.spinner("Por favor espere... Generando resumen de datos"):
            data, llm_summ, _ = summ.summarize(selected_dataset, my_config, my_client, encoding=selected_dataset_enc, summary_method=selected_method)
            st.session_state.data = data
            st.session_state.llm_summ = llm_summ
            st.session_state.selected_persona = None
            st.session_state.llm_personas = None
            st.session_state.user_persona_input = ""
            st.session_state.selected_goal = None
            st.session_state.llm_goals = None
            st.session_state.user_goal_input = ""
            st.session_state.charts = None
            st.session_state.goals_with_code = None

# Mostrar resumen si existe
if st.session_state.llm_summ:
    st.write("## Resumen")
    if "llm_desc" in st.session_state.llm_summ:
        st.write(st.session_state.llm_summ["llm_desc"])
    if "fields" in st.session_state.llm_summ:
        nfields_df = utils.summarize_properties_to_df(st.session_state.llm_summ["fields"])
        st.write(nfields_df)
    else:
        st.write(str(st.session_state.llm_summ))

    # Personas
    st.sidebar.write("### Personas interesadas en los datos")
    personas_radio = st.sidebar.radio(
        "¿Cómo definir a las personas interesadas en los datos?",
        ["Por defecto", "Generadas (LLM)", "Personalizada"],
        index=0,
        horizontal=True,
    )

    if personas_radio == "Por defecto":
        default_persona = "Un analista de datos muy capacitado capaz de plantear objetivos complejos y precisos sobre los datos."
        with st.container(height=400, border=True):
            st.write("Persona por defecto")
            st.write("----------------------")
            st.write(f"*{default_persona}*")
            if st.button("Seleccionar", key="per_def"):
                st.session_state.selected_persona = default_persona
                st.session_state.selected_goal = None
                st.session_state.llm_goals = None
                st.session_state.user_goal_input = ""
                st.session_state.charts = None
                st.session_state.goals_with_code = None

    elif personas_radio == "Generadas (LLM)":
        num_personas = st.sidebar.slider("Número de personas a generar", min_value=1, max_value=3, value=1)
        gen_personas_button = st.sidebar.button("Generar Personas")
        if gen_personas_button:
            per = PersonaExplorer()
            with st.spinner("Por favor espere... Generando posibles personas interesadas..."):
                st.session_state.llm_personas = per.generate(st.session_state.llm_summ, my_config, my_client, n=num_personas)
        if st.session_state.llm_personas:
            personas_row1 = st.columns(3)
            for idx, col in enumerate(personas_row1[:num_personas]):
                if idx < len(st.session_state.llm_personas['personas']):
                    persona_data = st.session_state.llm_personas['personas'][idx]
                    with col.container(height=400, border=True):
                        st.write("Persona generada (LLM)")
                        st.write(f"*{persona_data['persona']}*")
                        st.write("----------------------")
                        st.write(f"*{persona_data['rationale']}*")
                        if st.button("Seleccionar", key=f"per_btn_{idx}"):
                            st.session_state.selected_persona = persona_data['persona']
                            st.session_state.selected_goal = None
                            st.session_state.llm_goals = None
                            st.session_state.user_goal_input = ""
                            st.session_state.charts = None
                            st.session_state.goals_with_code = None

    elif personas_radio == "Personalizada":
        if "user_persona_input" not in st.session_state:
            st.session_state.user_persona_input = ""
        persona_input = st.sidebar.text_input(
            "Describe a la persona", 
            value=st.session_state.user_persona_input,
            key="persona_input_custom"
        )      
        if st.sidebar.button("Agregar persona", key="ag_per_btn") and persona_input:
            st.session_state.user_persona_input = persona_input
        with st.container(height=400, border=True):
            st.write("Persona personalizada")
            st.write("----------------------")
            st.write(f"*{st.session_state.user_persona_input}*")
            if st.button("Seleccionar", key="per_user") and st.session_state.user_persona_input:
                st.session_state.selected_persona = st.session_state.user_persona_input
                st.session_state.selected_goal = None
                st.session_state.llm_goals = None
                st.session_state.user_goal_input = ""
                st.session_state.charts = None
                st.session_state.goals_with_code = None

    if st.session_state.selected_persona:
        #st.write(f"Persona actual: *{st.session_state.selected_persona}*")
        st.badge(f"Persona actual: {st.session_state.selected_persona}", icon=":material/check:", color="green")

    # Objetivos
    if st.session_state.selected_persona:
        st.sidebar.write("### Objetivos (Goals)")
        goals_radio = st.sidebar.radio(
            "¿Cómo definir los objetivos (goals) de visualización?",
            ["Manualmente", "Generados (LLM)"],
            index=0,
            horizontal=True,
        )

        if goals_radio == "Manualmente":
            usr_goal_input = st.sidebar.text_input("¿Qué deseas visualizar?", value=st.session_state.user_goal_input)
            if st.sidebar.button("Agregar objetivo", key="ag_obj_btn") and usr_goal_input:
                st.session_state.user_goal_input = usr_goal_input
            with st.container(height=400, border=True):
                st.write("Objetivo de visualización")
                st.write("----------------------")
                st.write(f"*{st.session_state.user_goal_input}*")
                if st.button("Seleccionar", key="user_goal_viz") and st.session_state.user_goal_input:
                    goal = GoalExplorer()
                    st.session_state.selected_goal = goal.generate_from_user_prompt(st.session_state.user_goal_input)
                    st.session_state.charts = None
                    st.session_state.goals_with_code = None

        elif goals_radio == "Generados (LLM)":
            num_goals = st.sidebar.slider("Número de objetivos (goals) a generar", min_value=1, max_value=3, value=3)
            gen_goals_button = st.sidebar.button("Generar objetivos (goals)")
            if gen_goals_button:
                goal = GoalExplorer()
                with st.spinner("Por favor espere... Generando objetivos (goals) de visualización..."):
                    st.session_state.llm_goals = goal.generate(st.session_state.llm_summ, my_config, my_client, persona=st.session_state.selected_persona, n=num_goals)
            if st.session_state.llm_goals:
                goals_row1 = st.columns(3)
                for idx, col in enumerate(goals_row1[:num_goals]):
                    if idx < len(st.session_state.llm_goals['goals']):
                        goal_data = st.session_state.llm_goals['goals'][idx]
                        with col.container(height=400, border=True):
                            st.write("Objetivo de visualización generado (LLM)")
                            st.write(goal_data['question'])
                            st.write("----------------------")
                            st.write(f"*{goal_data['visualization']}*")
                            st.write("----------------------")
                            st.write(f"*{goal_data['rationale']}*")
                            if st.button("Seleccionar", key=f"gen_goal_viz_{idx}"):
                                st.session_state.selected_goal = {"goals": [goal_data]}
                                st.session_state.charts = None
                                st.session_state.goals_with_code = None

        if st.session_state.selected_goal:
            #st.write(f"Objetivo actual: *{st.session_state.selected_goal['goals'][0]['question']}*")
            st.badge(f"Objetivo actual: {st.session_state.selected_goal['goals'][0]['question']}", icon=":material/check:", color="green")

        # Visualizaciones
        if st.session_state.selected_goal:
            st.write("## Visualizaciones")
            st.info('Asegúrese de seleccionar y verificar el objetivo de visualización', icon="ℹ️")
            gen_viz_button = st.button("Generar Visualización")
            
            if gen_viz_button:
                with st.spinner("Por favor espere... Generando la visualización..."):
                    vizgen = VizGenerator()
                    st.session_state.goals_with_code, _ = vizgen.generate(st.session_state.llm_summ, st.session_state.selected_goal, my_config, my_client, library=selected_library)
                
                #st.write("Código generado para ejecutar:")
                #st.write(st.session_state.goals_with_code['goals'][0]['code'])
                
                with st.spinner("Por favor espere... Construyendo la visualización..."):
                    chart_ex = ChartExecutor()
                    try:
                        st.session_state.charts = chart_ex.execute(
                            st.session_state.data,
                            st.session_state.llm_summ,
                            in_goals_with_code=st.session_state.goals_with_code,
                            library=selected_library,
                            timeout_seconds=30
                        )
                    except Exception as e:
                        st.error(f"Error inesperado al construir la visualización: {str(e)}")
                        st.session_state.charts = None
                
                st.session_state.edit_prompt = None
                st.session_state.repair_code = None
                st.session_state.show_edit_input = False
                st.session_state.do_repair = False
            
            # Reintento para Generar Visualización
            if st.session_state.charts and not st.session_state.charts[0].status and "Timeout" in st.session_state.charts[0].error["message"]:
                st.error("La generación de la visualización tomó demasiado tiempo y fue interrumpida.")
                if st.button("Reintentar", key="retry_viz"):
                    st.session_state.charts = None
                    with st.spinner("Por favor espere... Reintentando la visualización..."):
                        chart_ex = ChartExecutor()
                        st.session_state.charts = chart_ex.execute(
                            st.session_state.data,
                            st.session_state.llm_summ,
                            in_goals_with_code=st.session_state.goals_with_code,
                            library=selected_library,
                            timeout_seconds=30
                        )
                    st.rerun()

            if st.session_state.charts and st.session_state.goals_with_code:
                if st.session_state.charts[0].status:
                    imgdata = base64.b64decode(st.session_state.charts[0].raster)
                    img = Image.open(io.BytesIO(imgdata))
                    st.image(img, caption=st.session_state.goals_with_code['goals'][0]['question'], use_container_width=True)
                    # st.pyplot(st.session_state.charts[0].figure, clear_figure=True)
                    # st.caption(st.session_state.goals_with_code['goals'][0]['question'])
                    
                    if st.button("Editar", key="edit_chart_btn"):
                        st.session_state.show_edit_input = True
                    
                    if st.session_state.show_edit_input:
                        edited_code_input = st.text_input(
                            "Instrucciones para la edición del gráfico",
                            value="",
                            placeholder="E.g: Utiliza colores pasteles...",
                            key="edit_viz_input"
                        )
                        if st.button("Aplicar cambios", key="apply_edit_btn"):
                            st.session_state.edit_prompt = edited_code_input
                            with st.spinner("Por favor espere... Aplicando cambios a la visualización..."):
                                vized = VizEditor()
                                edited_code = vized.generate(
                                    st.session_state.charts[0].code,
                                    st.session_state.llm_summ,
                                    st.session_state.edit_prompt,
                                    my_config,
                                    my_client, 
                                    library="seaborn"
                                )
                                goal_with_edited_code = {
                                    "goals": [{
                                        "index": st.session_state.charts[0].index,
                                        "question": st.session_state.charts[0].goal_question,
                                        "visualization": st.session_state.charts[0].goal_visualization,
                                        "rationale": st.session_state.charts[0].goal_rationale,
                                        "code": edited_code,
                                    }]
                                }         
                                
                                with st.spinner("Por favor espere... Construyendo la visualización editada..."):
                                    chart_ex = ChartExecutor()
                                    st.session_state.charts = chart_ex.execute(
                                        st.session_state.data,
                                        st.session_state.llm_summ,
                                        in_goals_with_code=goal_with_edited_code,
                                        library="seaborn",
                                        timeout_seconds=30
                                    )
                            
                            # Reintento para Editar
                            if not st.session_state.charts[0].status and "Timeout" in st.session_state.charts[0].error["message"]:
                                st.error("La edición de la visualización tomó demasiado tiempo y fue interrumpida.")
                                if st.button("Reintentar edición", key="retry_edit_btn"):
                                    with st.spinner("Por favor espere... Reintentando la edición..."):
                                        chart_ex = ChartExecutor()
                                        st.session_state.charts = chart_ex.execute(
                                            st.session_state.data,
                                            st.session_state.llm_summ,
                                            in_goals_with_code=goal_with_edited_code,
                                            library="seaborn",
                                            timeout_seconds=30
                                        )
                                    st.rerun()
                            elif st.session_state.charts[0].status:
                                st.session_state.show_edit_input = False
                                st.rerun()
                            else:
                                st.error("Algo ha fallado durante la edición de la visualización :c")
                                st.rerun()
                                
                    with st.expander("## Código de visualización", expanded=False):
                        st.code(st.session_state.charts[0].code)
                else:
                    st.error("Algo ha salido mal :c ¿Deseas intentar reparar la visualización?")
                    
                    if st.button("Reparar", key="repair_chart_btn"):
                        st.session_state.do_repair = True
                    
                    if st.session_state.do_repair:
                        goal_with_bad_edited_code = {
                            "goals": [{
                                "index": st.session_state.charts[0].index,
                                "question": st.session_state.charts[0].goal_question,
                                "visualization": st.session_state.charts[0].goal_visualization,
                                "rationale": st.session_state.charts[0].goal_rationale,
                                "code": st.session_state.charts[0].code,
                                "error_message": st.session_state.charts[0].error["message"],
                                "error_traceback": st.session_state.charts[0].error["traceback"]
                            }]
                        }
                        
                        with st.spinner("Por favor espere... Intentando reparar la visualización..."):
                            vizrep = VizRepairer()
                            repaired_code = vizrep.generate(
                                st.session_state.llm_summ,
                                goal_with_bad_edited_code["goals"][0]['code'],
                                goal_with_bad_edited_code["goals"][0]['error_message'],
                                goal_with_bad_edited_code["goals"][0]['error_traceback'],
                                my_config,
                                my_client, 
                                library="seaborn"
                            )
                            st.write(repaired_code)
                            
                            goal_with_repaired_code = {
                                "goals": [{
                                    "index": goal_with_bad_edited_code["goals"][0]['index'],
                                    "question": goal_with_bad_edited_code["goals"][0]['question'],
                                    "visualization": goal_with_bad_edited_code["goals"][0]['visualization'],
                                    "rationale": goal_with_bad_edited_code["goals"][0]['rationale'],
                                    "code": repaired_code,
                                }]
                            }    
                            
                            with st.spinner("Por favor espere... Construyendo la visualización reparada..."):
                                chart_ex = ChartExecutor()
                                st.session_state.charts = chart_ex.execute(
                                    st.session_state.data,
                                    st.session_state.llm_summ,
                                    in_goals_with_code=goal_with_repaired_code,
                                    library="seaborn",
                                    timeout_seconds=30
                                )
                        
                        # Reintento para Reparar
                        if not st.session_state.charts[0].status and "Timeout" in st.session_state.charts[0].error["message"]:
                            st.error("La reparación de la visualización tomó demasiado tiempo y fue interrumpida.")
                            if st.button("Reintentar reparación", key="retry_repair_btn"):
                                with st.spinner("Por favor espere... Reintentando la reparación..."):
                                    chart_ex = ChartExecutor()
                                    st.session_state.charts = chart_ex.execute(
                                        st.session_state.data,
                                        st.session_state.llm_summ,
                                        in_goals_with_code=goal_with_repaired_code,
                                        library="seaborn",
                                        timeout_seconds=30
                                    )
                                st.rerun()
                        elif st.session_state.charts[0].status:
                            st.session_state.do_repair = False
                            st.rerun()
                        else:
                            st.error("Algo ha fallado durante la reparación de la visualización :c")
                            st.error(st.session_state.charts[0].error["message"])
                            st.session_state.do_repair = False
                            st.rerun()