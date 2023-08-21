from fastapi import APIRouter
from api.routes.addresses import router as addresses_router
from api.routes.contracts import router as contracts_router
from api.routes.domains import router as domains_router

router = APIRouter()

router.include_router(addresses_router, prefix="/address", tags=["Addresses"])
router.include_router(contracts_router, prefix="/contract", tags=["Contracts"])
router.include_router(domains_router, prefix="/domain", tags=["Domains"])
