import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq

# Inicializa o FastAPI
app = FastAPI(title="O Conselheiro API", version="0.1.0")

# Configuração de CORS (Permite conexões do frontend)
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

# Função auxiliar para neutralizar termos confessionais e torná-los universais
def ecumenizar_texto(texto: str) -> str:
    if not texto:
        return texto
    # Substituições para tornar o texto puramente cristão/ecumênico
    texto = re.sub(r'\bCatólica\b', 'Cristã', texto)
    texto = re.sub(r'\bcatólica\b', 'cristã', texto)
    texto = re.sub(r'\bCatólico\b', 'Cristão', texto)
    texto = re.sub(r'\bcatólico\b', 'cristão', texto)
    return texto

# Rota para buscar o conselho estruturado na Groq
@app.post("/api/conselho")
async def obter_conselho(request: ConselhoRequest):
    system_instruction = (
        f"Você é O CONSELHEIRO, um mentor espiritual. Responda usando a técnica Feynman baseado na tradição {request.tradicao}. "
        f"Divida obrigatoriamente a resposta em quatro blocos utilizando títulos em Markdown: "
        f"#### **Em poucas palavras:**, #### **Imagine assim:**, #### **O que diz a Minha Palavra:** e #### **Para o seu dia a dia:**. "
        f"Seja acolhedor, ecumênico, focado no amor de Cristo e fale em primeira pessoa."
    )
    
    try:
        # Usando o modelo de produção oficial e ativo na plataforma da Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": request.pergunta}
            ],
            model="openai/gpt-oss-20b",
            temperature=0.3,
        )
        
        # Leitura estruturada e resiliente da resposta
        try:
            conselho = chat_completion.choices[0].message.content
        except (AttributeError, TypeError, IndexError):
            try:
                conselho = chat_completion.choices['message']['content']
            except Exception:
                try:
                    conselho = chat_completion.choices[0].message.content
                except Exception as e:
                    conselho = f"#### **Erro de Processamento:**\nNão consegui extrair o texto. Detalhe: {str(e)}"

        # Aplica a higienização de termos antes de devolver para a interface do usuário
        conselho_higienizado = ecumenizar_texto(conselho)

        return {"conselho": conselho_higienizado}

    except Exception as e:
        # Retorna o erro detalhado diretamente para ajudar no diagnóstico visual
        return {"conselho": f"#### **Erro de Comunicação com a Groq:**\n{str(e)}"}

# --- CONFIGURAÇÃO DA INTERFACE VISUAL ---

@app.get("/")
def home():
    caminhos_possiveis = [
        "index.html", 
        "templates/index.html", 
        "Index.html"
    ]
    
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            return FileResponse(caminho)
            
    return {
        "status": "API Online, mas o arquivo index.html não foi achado na raiz.",
        "dica": "Verifique se o nome do arquivo no seu GitHub está exatamente minúsculo como index.html"
    }
