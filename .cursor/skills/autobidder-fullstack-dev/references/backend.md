# Backend Reference — FastAPI + PostgreSQL + JWT

## Project Structure

```
backend/
├── app/
│   ├── main.py             # App entrypoint, router registration, CORS, middleware
│   ├── core/
│   │   ├── auth.py         # JWT encode/decode, get_current_user dependency
│   │   ├── config.py       # Settings (pydantic-settings, reads from .env)
│   │   ├── database.py     # Async SQLAlchemy engine + get_db dependency
│   │   └── exceptions.py   # handle_errors decorator, custom exception classes
│   ├── routers/            # One file per domain
│   │   ├── auth.py         # POST /auth/login, /auth/register, /auth/refresh
│   │   ├── proposals.py    # CRUD + /generate endpoint
│   │   ├── knowledge.py    # /search, /upload, /stats
│   │   └── emails.py       # /send
│   ├── schemas/            # Pydantic v2 request/response models
│   ├── models/             # SQLAlchemy ORM models
│   └── services/           # Business logic (AI calls, RAG, email)
│       ├── proposal_service.py
│       ├── knowledge_service.py
│       └── email_service.py
└── requirements.txt
```

## Router Registration (main.py pattern)

```python
from app.routers import auth, proposals, knowledge, emails

app.include_router(auth.router,       prefix="/api/auth",      tags=["auth"])
app.include_router(proposals.router,  prefix="/api/proposals", tags=["proposals"])
app.include_router(knowledge.router,  prefix="/api/knowledge", tags=["knowledge"])
app.include_router(emails.router,     prefix="/api/emails",    tags=["emails"])
```

## Pydantic v2 Schema Conventions

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProposalCreate(BaseModel):
    job_description: str = Field(..., min_length=50)
    tone: str = Field(default="casual", pattern="^(casual|technical|formal|nontechnical)$")
    focus_angle: Optional[str] = None

class ProposalResponse(BaseModel):
    id: str
    content: str
    word_count: int
    created_at: datetime
    
    model_config = {"from_attributes": True}  # replaces orm_mode in v2
```

## Database / SQLAlchemy Pattern

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Async query pattern
```python
from sqlalchemy import select

async def get_proposals_for_user(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(Proposal)
        .where(Proposal.user_id == user_id)
        .order_by(Proposal.created_at.desc())
    )
    return result.scalars().all()
```

## JWT Auth

```python
# app/core/auth.py
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expire}, settings.SECRET_KEY, algorithm="HS256")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Service Layer Pattern

Business logic lives in `app/services/`, NOT in routers. Routers are thin.

```python
# app/services/proposal_service.py
class ProposalService:
    def __init__(self, db: AsyncSession, knowledge_service: KnowledgeService):
        self.db = db
        self.ks = knowledge_service

    async def generate(self, user: User, req: ProposalCreate) -> str:
        # 1. RAG retrieval
        context = await self.ks.search(req.job_description, user_id=user.id)
        # 2. Build prompt
        prompt = build_prompt(req, context)
        # 3. Call LLM
        response = await call_openai(prompt)  # or call_deepseek()
        # 4. Persist
        proposal = Proposal(user_id=user.id, content=response, ...)
        self.db.add(proposal)
        await self.db.commit()
        return response

# Router delegates to service:
@router.post("/generate", response_model=ProposalResponse)
async def generate(body: ProposalCreate, user: User = Depends(get_current_user), db = Depends(get_db)):
    svc = ProposalService(db, KnowledgeService(db))
    content = await svc.generate(user, body)
    return {"content": content, ...}
```

## Database Migrations

Migrations live in `database/migrations/` as raw SQL files.

```sql
-- database/migrations/0004_add_proposal_tone.sql
ALTER TABLE proposals ADD COLUMN tone VARCHAR(20) DEFAULT 'casual';
ALTER TABLE proposals ADD COLUMN word_count INTEGER;
```

Apply: `bash scripts/migrate.sh` (wraps `psql` with the correct connection string)

When adding a new column:
1. Write the migration SQL
2. Update the SQLAlchemy model in `app/models/`
3. Update the Pydantic schemas in `app/schemas/`
4. Restart the backend container

## Email via Resend

```python
# app/services/email_service.py
import resend

resend.api_key = settings.RESEND_API_KEY

async def send_proposal_email(to: str, subject: str, html: str):
    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to],
        "bcc": [settings.RESEND_BCC_EMAIL],  # always BCC for archiving
        "subject": subject,
        "html": html,
    })
```
