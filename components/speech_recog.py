import torch
import torchaudio
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

print("Cargando: openai/whisper-large-v3-turbo por defecto")
model_id = "openai/whisper-large-v3-turbo"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    model_kwargs={"language": "es"}
)

def select_ASRModel(model_str):
    print("Cambiando a modelo:", model_str)
    global model, processor, pipe

    if "openai" in model_str or "facebook" in model_str:
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_str,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        ).to(device)

        processor = AutoProcessor.from_pretrained(model_str)

        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
        )

    #Comentado debido a la inestabilidad de modelos de nvidia en Windows
    #elif "nvidia" in model_str:
        #from nemo.collections.asr.models import EncDecRNNTBPEModel
        #model = EncDecRNNTBPEModel.from_pretrained(model_name=model_str)
        #pipe = None




def convert_to_asraudio(file):
   
    print("Inicio de conversión de audio a formato válido para Whisper...")

    waveform, sr = torchaudio.load(file)

    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        waveform = resampler(waveform)

    print("Audio preparado para ser convertido a numpy.")
    # Convertir el audio a un array de numpy de tipo float32
    raw_audio = waveform.squeeze().numpy().astype(np.float32)

    return raw_audio


def transcribe_audio(file):

    raw_audio = convert_to_asraudio(file)

    print("Enviando audio a modelo de transcripción...")

    result = pipe(raw_audio)
    return result["text"]


