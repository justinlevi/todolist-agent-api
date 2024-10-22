from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from src.graphql.schema import schema
from prisma import Prisma
from prisma.errors import PrismaError
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.middleware.gzip import GZipMiddleware
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from slowapi.middleware import SlowAPIMiddleware
from src.api import chat
from src.config import settings
from src.logger import get_logger
from src.api import models
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.openapi.utils import get_openapi
from src.utils.helpers import get_current_timestamp
from src.graphql.context import GraphQLContext, get_context


# limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="A production-grade FastAPI API designed for building chatbots.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
# ALLOWED_ORIGINS is used to specify which origins can access your API from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# # Add SlowAPI middleware
# app.add_middleware(SlowAPIMiddleware)

# Add Gzip compression
# app.add_middleware(GZipMiddleware, minimum_size=1000, exclude_paths=["/v1/chat/completions"])

logger = get_logger()


graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)
app.include_router(graphql_app, prefix="/graphql")

app.include_router(models.router, tags=["Models"])
app.include_router(chat.router, tags=["Chat"])


async def init_db():
    async with Prisma() as db:
        try:
            await db.connect()
        except PrismaError as e:
            if "Already connected" in str(e):
                # Connection already exists, so we can proceed
                pass
            else:
                # Re-raise the exception if it's not the "Already connected" error
                raise


@app.get("/")
async def root(request: Request):
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Chatbot API"}


@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("Application startup")


@app.on_event("shutdown")
async def shutdown_event():
    async with Prisma() as db:
        await db.disconnect()
    logger.info("Application shutdown")


# Add security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


# Trusted Host Middleware
# ALLOWED_HOSTS is likely used to validate incoming requests server side
if settings.ENVIRONMENT != "test":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# HTTPS Redirect Middleware (only in production)
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="A production-grade FastAPI API designed for building chatbots.",
        routes=app.routes,
    )
    openapi_schema["paths"]["/health"] = {
        "get": {
            "summary": "Health Check",
            "operationId": "health_check",
            "responses": {
                "200": {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "version": {"type": "string"},
                                    "timestamp": {"type": "integer"},
                                },
                            }
                        }
                    },
                }
            },
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": get_current_timestamp(),
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # logger.debug(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    # logger.debug(f"Returning response: {response.status_code}")
    return response


# @app.options("/")
# async def options_root():
#     return Response(status_code=200)
