import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="O Conselheiro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Sua_Chave_Gemini = "AQ.Ab8RN6Jcmc7AJrGfeFHDctyZenUh1AXS3S5iM3_gwfwlopTydg"
client = genai.Client(api_key=Sua_Chave_Gemini)

DB_USUARIOS = {}

class PerguntaRequest(BaseModel):
    usuario_id: str
    pergunta: str
    tradicao: str

@app.post("/api/conselho")
async def obter_conselho(request: PerguntaRequest):
    uid = request.usuario_id
    if uid not in DB_USUARIOS: 
        DB_USUARIOS[uid] = {"perguntas_restantes": 3, "is_membro": False}
    
    usuario = DB_USUARIOS[uid]
    
    if not usuario["is_membro"] and usuario["perguntas_restantes"] <= 0:
        return {"bloqueado": True, "resposta": "#### **Limite Atingido**\n\nVocê alcançou seu limite diário gratuito."}
    
    system_instruction = f"Você é O CONSELHEIRO, um mentor espiritual. Responda usando a técnica Feynman baseado na tradição {request.tradicao}. Divida obrigatoriamente a resposta em quatro blocos utilizando títulos em Markdown: #### **Em poucas palavras:**, #### **Imagine assim:**, #### **O que diz a Minha Palavra:** e #### **Para o seu dia a dia:**. Seja acolhedor e fale em primeira pessoa."
    
    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=request.pergunta,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3
            )
        )
        
        if not usuario["is_membro"]: 
            usuario["perguntas_restantes"] -= 1
            
        return {
            "bloqueado": False, 
            "resposta": response.text, 
            "perguntas_restantes": usuario["perguntas_restantes"]
        }
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))
