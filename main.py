import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

# Inicializa o FastAPI
app = FastAPI(title="O Conselheiro API", version="0.1.0")

# Configuração de CORS (Permite que o app seja acessado de qualquer lugar, inclusive celulares)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração 100% segura recomendada pelo GitHub e Render
# O código lê a chave diretamente da memória do servidor do Render de forma invisível
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Estrutura de dados que a API recebe (Request Body)
class ConselhoRequest(BaseModel):
    usuario_id: str
    pergunta: str
    tradicao: str

# Rota principal para obter o conselho estruturado
@app.post("/api/conselho")
async def obter_conselho(request: ConselhoRequest):
    # O seu prompt espetacular usando a técnica Feynman nos 4 blocks estruturados
    system_instruction = (
        f"Você é O CONSELHEIRO, um mentor espiritual. Responda usando a técnica Feynman baseado na tradição {request.tradicao}. "
        f"Divida obrigatoriamente a resposta em quatro blocos utilizando títulos em Markdown: "
        f"#### **Em poucas palavras:**, #### **Imagine assim:**, #### **O que diz a Minha Palavra:** e #### **Para o seu dia a dia:**. "
        f"Seja acolhedor e fale em primeira pessoa."
    )
    
    try:
        # Chamada ultra-rápida na infraestrutura da Groq
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
        
        # Extrai o texto gerado pela IA e retorna para o usuário
        conselho = chat_completion.choices.message.content
        return conselho

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no Conselheiro: {str(e)}")

# Rota simples de teste para garantir que a API está viva
@app.get("/")
def home():
    return {"status": "O Conselheiro está online e operando com a Groq!"}
