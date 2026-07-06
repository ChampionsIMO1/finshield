from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.transactions import router as transactions_router

app = FastAPI(title="SphinxGuard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "SphinxGuard API is running"}

@app.get("/health")
def health():
    return {"message": "ok"}