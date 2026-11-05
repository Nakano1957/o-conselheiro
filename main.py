import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq

# Inicializa o FastAPI
app = FastAPI(title="O Conselheiro API", version="0.1.0")

# Configuração de CORS (Permite que o app seja acessado de qualquer lugar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração segura da API da Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Estrutura de dados que a API recebe (Request Body)
class ConselhoRequest(BaseModel):
    usuario_id: str
    pergunta: str
    tradicao: str

# Rota para buscar o conselho estruturado na Groq
@app.post("/api/conselho")
async def obter_conselho(request: ConselhoRequest):
    system_instruction = (
        f"Você é O CONSELHEIRO, um mentor espiritual. Responda usando a técnica Feynman baseado na tradição {request.tradicao}. "
        f"Divida obrigatoriamente a resposta em quatro blocos utilizando títulos em Markdown: "
        f"#### **Em poucas palavras:**, #### **Imagine assim:**, #### **O que diz a Minha Palavra:** e #### **Para o seu dia a dia:**. "
        f"Seja acolhedor e fale em primeira pessoa."
    )
    
    try:
        # ATUALIZADO: Usando o modelo oficial, rápido e estável da Groq (Llama 3.3)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": request.pergunta
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
        )
        
        try:
            conselho = chat_completion.choices[0].message.content
        except (AttributeError, TypeError):
            try:
                conselho = chat_completion.choices[0]['message']['content']
            except Exception:
                conselho = str(chat_completion)

        return {"conselho": conselho}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no Conselheiro: {str(e)}")

# --- CONFIGURAÇÃO DA INTERFACE VISUAL ---

# Verifica se a pasta 'templates' ou onde estão seus arquivos HTML existe
# Se você tiver arquivos CSS/JS numa pasta chamada 'static', descomente a linha abaixo:
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    # Procura pelo arquivo index.html na raiz do projeto
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    # Se o index.html estiver dentro de uma pasta chamada 'templates', mudamos para "templates/index.html"
    elif os.path.exists("templates/index.html"):
        return FileResponse("templates/index.html")
    else:
        return {"status": "API Online, mas o arquivo index.html não foi encontrado na raiz do projeto!"}
