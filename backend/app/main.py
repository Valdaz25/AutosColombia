
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routers.auth import router as auth_router
from app.routers.usuarios import router as usuarios_router
from app.routers.vehiculos import router as vehiculos_router
from app.routers.celdas import router as celdas_router
from app.routers.operadores import router as operadores_router
from app.routers.estancias import router as estancias_router

from app.services.auth import AuthError
from app.services.usuario import UsuarioError
from app.services.vehiculo import VehiculoError
from app.services.celda import CeldaError
from app.services.operador import OperadorError
from app.services.estancia import EstanciaError


app = FastAPI(title="Autos Colombia API")


# Registro de rutas
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(vehiculos_router)
app.include_router(celdas_router)
app.include_router(operadores_router)
app.include_router(estancias_router)


# Manejo de errores
@app.exception_handler(AuthError)
@app.exception_handler(UsuarioError)
@app.exception_handler(VehiculoError)
@app.exception_handler(CeldaError)
@app.exception_handler(OperadorError)
@app.exception_handler(EstanciaError)
async def entity_error_handler(
    request,
    error: AuthError | UsuarioError | VehiculoError | CeldaError | OperadorError | EstanciaError,
) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"detail": error.detail},
    )


# Verificación de funcionamiento
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
