from fastapi import APIRouter

from app.api.v1.endpoints import cartao

router = APIRouter()

router.include_router(cartao.router, prefix="/cartoes", tags=["Cartão"])
