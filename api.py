from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# CORS configuration
origins = ["*"]  # Para teste, mas ajuste para a origem correta em produção

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

site_statuses = []

@app.get("/api/status")
async def get_status():
    """Retorna o status atual dos sites."""
    return site_statuses

@app.post("/api/update_status")
async def update_status(status_data: list):
    """Atualiza o status dos sites."""
    global site_statuses
    site_statuses = status_data
    return {"message": "Status atualizado com sucesso"}
