from fastapi import APIRouter

from api.routes.contracts import router as contracts_router
from api.routes.domains import router as domains_router

router = APIRouter()

router.include_router(contracts_router, prefix="/blocklist")
router.include_router(domains_router, prefix="/blocklist")