from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.template_routes import router as template_router
from app.api.classifier_routes import router as classifier_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(template_router, prefix="/template")
app.include_router(classifier_router, prefix="/classifier")
