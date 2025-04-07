import ast
import base64
import importlib
import io
import os
import re
import traceback
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pandas as pd
import copy
import threading
import queue

from dataclasses import field
from typing import Any, Dict, List, Optional, Union
from pydantic.dataclasses import dataclass

@dataclass
class ChartExecutorResponse:
    """Response from a visualization execution"""
    index: Optional[int]
    goal_question: Optional[str]
    goal_visualization: Optional[str]
    goal_rationale: Optional[str]
    spec: Optional[Union[str, Dict]]
    status: bool
    raster: Optional[str]
    code: str
    library: str
    error: Optional[Dict] = None

    def _repr_mimebundle_(self, include=None, exclude=None):
        bundle = {"text/plain": self.code}
        if self.raster is not None:
            bundle["image/png"] = self.raster
        if self.spec is not None:
            bundle["application/vnd.vegalite.v5+json"] = self.spec
        return bundle

    def savefig(self, path):
        if self.raster:
            with open(path, 'wb') as f:
                f.write(base64.b64decode(self.raster))
        else:
            raise FileNotFoundError("No raster image to save")

def preprocess_code(code):
    code = code.replace("<imports>", "").replace("<stub>", "").replace("<transforms>", "").replace("python", "")
    if "chart = plot(data)" in code:
        index = code.find("chart = plot(data)")
        if index != -1:
            code = code[:index + len("chart = plot(data)")]
    if "```" in code:
        pattern = r"```(?:\w+\n)?([\s\S]+?)```"
        matches = re.findall(pattern, code)
        if matches:
            code = matches[0]
    if "import" in code:
        index = code.find("import")
        if index != -1:
            code = code[index:]
    code = code.replace("```", "")
    if "chart = plot(data)" not in code:
        code = code + "\nchart = plot(data)"
    return code

def get_globals_dict(code_string, data):
    tree = ast.parse(code_string)
    imported_modules = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = importlib.import_module(alias.name)
                imported_modules.append((alias.name, alias.asname, module))
        elif isinstance(node, ast.ImportFrom):
            module = importlib.import_module(node.module)
            for alias in node.names:
                obj = getattr(module, alias.name)
                imported_modules.append((f"{node.module}.{alias.name}", alias.asname, obj))
    globals_dict = {}
    for module_name, alias, obj in imported_modules:
        if alias:
            globals_dict[alias] = obj
        else:
            globals_dict[module_name.split(".")[-1]] = obj
    ex_dicts = {"pd": pd, "data": data, "plt": plt}
    globals_dict.update(ex_dicts)
    return globals_dict

class ChartExecutor:
    def __init__(self) -> None:
        pass

    def _run_execution(self, code, ex_locals, data, library, goal, queue_result):
        """Ejecuta el código y guarda el resultado en una cola"""
        try:
            print("Paso 4: Ejecutando código")
            exec(code, ex_locals)
            print("Paso 5: Código ejecutado")
            
            print("Paso 6: Verificando 'chart'")
            if "chart" not in ex_locals:
                raise ValueError("El código no definió la variable 'chart'")
            chart = ex_locals["chart"]
            
            # print("Paso 7: Generando imagen")
            
            # print("Paso 7.2: Configurando figura")
            # fig = chart
            # if not fig.get_axes():
            #     raise ValueError("No hay ejes en la figura para renderizar")
            
            # fig.gca().set_frame_on(False)
            # fig.gca().grid(color="lightgray", linestyle="dashed", zorder=-10)
            # fig.tight_layout()
            
            # print("Paso 7.3: Renderizando imagen")
            # canvas = FigureCanvasAgg(fig)
            # buf = io.BytesIO()
            # canvas.print_png(buf)
            # print("Paso 8: Imagen guardada en buffer")
            # buf.seek(0)
            # plot_data = base64.b64encode(buf.read()).decode("ascii")
            # print("Paso 9: Imagen codificada en base64")

            print("Paso 7: Generando imagen")
            buf = io.BytesIO()
            plt.gca().set_frame_on(False)
            plt.grid(color="lightgray", linestyle="dashed", zorder=-10)
            plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
            print("Paso 8: Imagen guardada en buffer")
            buf.seek(0)
            plot_data = base64.b64encode(buf.read()).decode("ascii")
            print("Paso 9: Imagen codificada en base64")
            
            result = ChartExecutorResponse(
                index=goal["index"],
                goal_question=goal["question"],
                goal_visualization=goal["visualization"],
                goal_rationale=goal["rationale"],
                spec=None,
                status=True,
                raster=plot_data,
                code=code,
                library=library,
            )
        except Exception as exception_error:
            print(f"Error en ejecución:\n{str(exception_error)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            result = ChartExecutorResponse(
                index=goal["index"],
                goal_question=goal["question"],
                goal_visualization=goal["visualization"],
                goal_rationale=goal["rationale"],
                spec=None,
                status=False,
                raster=None,
                code=code,
                library=library,
                error={
                    "message": str(exception_error),
                    "traceback": traceback.format_exc(),
                },
            )
        finally:
            plt.close('all')
            print("Paso 10: Estado limpiado")
        
        queue_result.put(result)

    def execute(
        self,
        data,
        summary,
        in_goals_with_code=None,
        library="seaborn",
        return_error=True,
        timeout_seconds=10,
    ):
        charts = []
        goals_with_code = copy.deepcopy(in_goals_with_code)
        
        if library not in ["matplotlib", "seaborn"]:
            raise Exception(
                f"Unsupported library. Supported libraries are seaborn, matplotlib. You provided {library}"
            )

        for goal in goals_with_code["goals"]:
            code = preprocess_code(goal["code"])
            print(f"Paso 1: Código preprocesado:\n{code}")
            
            try:
                print("Paso 2: Limpiando estado de matplotlib")
                plt.clf()
                plt.close('all')
                
                print("Paso 3: Preparando globals")
                ex_locals = get_globals_dict(code, data)
                
                queue_result = queue.Queue()
                thread = threading.Thread(
                    target=self._run_execution,
                    args=(code, ex_locals, data, library, goal, queue_result)
                )
                thread.start()
                thread.join(timeout=timeout_seconds)
                
                if thread.is_alive():
                    print(f"Timeout: La ejecución excedió {timeout_seconds} segundos")
                    # No podemos matar el hilo directamente en Python, pero marcamos el timeout
                    charts.append(
                        ChartExecutorResponse(
                            index=goal["index"],
                            goal_question=goal["question"],
                            goal_visualization=goal["visualization"],
                            goal_rationale=goal["rationale"],
                            spec=None,
                            status=False,
                            raster=None,
                            code=code,
                            library=library,
                            error={
                                "message": f"Timeout: La ejecución excedió {timeout_seconds} segundos",
                                "traceback": "",
                            },
                        )
                    )
                else:
                    result = queue_result.get_nowait()
                    charts.append(result)
                
            except Exception as exception_error:
                print(f"Error inesperado:\n{str(exception_error)}")
                print(f"Traceback:\n{traceback.format_exc()}")
                if return_error:
                    charts.append(
                        ChartExecutorResponse(
                            index=goal["index"],
                            goal_question=goal["question"],
                            goal_visualization=goal["visualization"],
                            goal_rationale=goal["rationale"],
                            spec=None,
                            status=False,
                            raster=None,
                            code=code,
                            library=library,
                            error={
                                "message": str(exception_error),
                                "traceback": traceback.format_exc(),
                            },
                        )
                    )
            finally:
                plt.close('all')
                print("Paso 11: Estado limpiado")
        
        print("Paso 12: Ejecución completada")
        return charts