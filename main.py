import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="O Conselheiro API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class ConselhoRequest(BaseModel):
    usuario_id: str
    pergunta: str
    tradicao: str

def ecumenizar_texto(texto: str) -> str:
    if not texto:
        return texto
    texto = re.sub(r'\bCatólica\b', 'Cristã', texto)
    texto = re.sub(r'\bcatólica\b', 'cristã', texto)
    texto = re.sub(r'\bCatólico\b', 'Cristão', texto)
    texto = re.sub(r'\bcatólico\b', 'cristão', texto)
    return texto

@app.post("/api/conselho")
async def obter_conselho(request: ConselhoRequest):
    system_instruction = (
        f"Você é O CONSELHEIRO, um mentor espiritual. Responda usando a técnica Feynman baseado na tradição {request.tradicao}. "
        f"Divida obrigatoriamente a resposta em quatro blocos utilizando títulos em Markdown: "
        f"#### **Em poucas palavras:**, #### **Imagine assim:**, #### **O que diz a Minha Palavra:** e #### **Para o seu dia a dia:**. "
        f"Seja acolhedor, ecumênico, focado no amor de Cristo, baseado em princípios cristãos e fale em primeira pessoa."
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": request.pergunta}
            ],
            model="openai/gpt-oss-20b",
            temperature=0.3,
        )
        try:
            conselho = chat_completion.choices[0].message.content
        except Exception:
            try:
                conselho = chat_completion.choices['choices'][0]['message']['content']
            except Exception as e:
                conselho = f"#### **Erro de Processamento:**\nNão consegui extrair o texto. Detalhe: {str(e)}"
        return {"conselho": ecumenizar_texto(conselho)}
    except Exception as e:
        return {"conselho": f"#### **Erro de Comunicação com a Groq:**\n{str(e)}"}

@app.get("/")
def home():
    for caminho in ["index.html", "templates/index.html", "Index.html"]:
        if os.path.exists(caminho):
            return FileResponse(caminho)
    return {"status": "API Online, mas o index.html não foi achado."}

