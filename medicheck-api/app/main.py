from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.routes.session import router as session_router
from app.routes.auth import router as auth_router
from app.routes.consents import router as consents_router
from app.routes.notes import router as notes_router
from app.routes.reminders import router as reminders_router
from app.routes.symptoms import router as symptoms_router
from app.routes.patient_records import router as patient_records_router
from app.routes.doctor_notes import router as doctor_notes_router
from app.routes.messages import router as messages_router
from app.routes.rules import router as rules_router

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(session_router)
app.include_router(auth_router)
app.include_router(consents_router)
app.include_router(notes_router)
app.include_router(reminders_router)
app.include_router(symptoms_router)
app.include_router(patient_records_router)
app.include_router(doctor_notes_router)
app.include_router(messages_router)
app.include_router(rules_router)

@app.get("/health")
def health():
    return {"ok": True}
