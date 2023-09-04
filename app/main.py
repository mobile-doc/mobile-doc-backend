from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    status,
    patient,
    medicine,
    session,
    doctor,
    authentication,
    test_result,
    random_router,
)
from .constants import PROJECT_NAME, VERSION_NAME


def start_application(title, version):
    application = FastAPI(title=title, version=version)
    application.include_router(status.router)
    application.include_router(authentication.router)
    application.include_router(patient.router)
    application.include_router(medicine.router)
    application.include_router(session.router)
    application.include_router(doctor.router)
    application.include_router(test_result.router)
    application.include_router(random_router.router)
    return application


app = start_application(title=PROJECT_NAME, version=VERSION_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
