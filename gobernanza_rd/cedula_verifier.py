"""Standalone local cédula cross-verification service.

Run:
    cd gobernanza_rd
    uvicorn cedula_verifier:app --host 0.0.0.0 --port 8001

The Vercel frontend can point VITE_CEDULA_VERIFY_URL at this service to use
the local AI (Ollama) as an additional validator.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.cedula import mask_cedula, normalize_cedula
from utils.cedula_cross_validator import (
    cross_validate,
    load_credential,
    verify_with_local_ai,
)

app = FastAPI(title="DOM.gov Cédula Cross-Verifier", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerifyRequest(BaseModel):
    cedula: str
    barcode: str | None = None


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "cedula-cross-verifier"}


@app.get("/credential")
def credential() -> dict[str, Any]:
    cred = load_credential()
    return {
        "role": cred.get("role"),
        "masked_cedula": mask_cedula(normalize_cedula(cred.get("cedula"))),
        "barcode": cred.get("barcode"),
        "source": cred.get("source", "file"),
    }


@app.post("/verify")
def verify(request: VerifyRequest) -> dict[str, Any]:
    deterministic = cross_validate(request.cedula, request.barcode or "")
    local_ai = verify_with_local_ai(request.cedula, request.barcode or "", deterministic)
    return {"deterministic": deterministic, "local_ai": local_ai}