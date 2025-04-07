import json
from openai import OpenAI

def load_llm_client(config, provider="vllm"):
    """
    Crear el cliente con el proveedor seleccionado.
    Devuelve la configuración del yaml y el cliente
    """
    if provider == "vllm":
        client = OpenAI(
            base_url = config["vllm_config"]["vllm_base_url"],
            api_key = config["api_keys"]["vllm"]
        )
        config["dynamic_config"]["dynamic_model_name"] = config["vllm_config"]["vllm_model_name"] 

        return config, client
        
    elif provider == "openrouter":
        client = OpenAI(
            base_url=config["openrouter_config"]["openrouter_base_url"],
            api_key=config["api_keys"]["openrouter"]
        )
        config["dynamic_config"]["dynamic_model_name"] = config["openrouter_config"]["openrouter_model_name"] 

        return config, client

    else:
        return None, None


def get_llm_answer(client, model, messages, guided_json=None):
    """
    Realiza la petición al proveedor y devuelve la respuesta
    del llm
    """
    answer = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=1.0,
        extra_body={
            'repetition_penalty': 1,
            'top_p': 0.95,
            #'frequency_penalty': 0,
            #'presence_penalty': 0,
            'top_k': 64,
            'min_p': 0.0,
            #'do_sample': True,
            #'seed':42,
            'max_tokens': 4096,
            'guided_json': guided_json
        })
    
    return answer.choices[0].message.content.strip()
        