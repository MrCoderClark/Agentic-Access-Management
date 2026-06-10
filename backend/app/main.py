from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import health, users, systems, policies, tickets, grants, audit, documents, access_requests, agents
from app.core.exceptions import AppError, app_error_handler, unhandled_error_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="AgentGuard API",
    description="AI-native Access Governance & ITSM Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Error handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, tags=["health"])
app.include_router(users.router)
app.include_router(systems.router)
app.include_router(policies.router)
app.include_router(tickets.router)
app.include_router(grants.router)
app.include_router(audit.router)
app.include_router(documents.router)
app.include_router(access_requests.router)
app.include_router(agents.router)
