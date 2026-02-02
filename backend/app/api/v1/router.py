from app.api.v1.endpoints import auth, market, ai_firm

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(ai_firm.router, prefix="/ai-firm", tags=["ai-firm"])
