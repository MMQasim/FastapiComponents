# main.py
from fastapi import FastAPI
from fastapicomponents.auth.routes import get_auth_router
from fastapicomponents.db_module.database import SessionLocal, engine
from fastapicomponents.user_module.models import Base
from fastapicomponents.user_module.routers import router as user_router
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup logic ---
    print("✅ Initializing database...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    app.state.db = db  # store globally if you want
    print("✅ Database ready")

    yield  # app runs between startup and shutdown

    # --- Shutdown ---
    print("🛑 Closing DB session")
    db.close()

app = FastAPI(lifespan=lifespan)

# dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize providers and register auth router
db = next(get_db())
auth_router = get_auth_router()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router)
