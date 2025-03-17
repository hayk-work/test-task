from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from users.routes import router as user_router
from documents.routes import router as documents_router

app = FastAPI()


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(documents_router, prefix="/documents", tags=["documents"])
