from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.core.db import get_conn
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest):
    email = payload.email.lower().strip()
    password = payload.password
    role = payload.role

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        pw_hash = hash_password(password)

        # Create user
        cur.execute(
            """
            INSERT INTO users (email, password_hash, role)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (email, pw_hash, role),
        )
        user_id = cur.fetchone()["id"]
        conn.commit()

    token = create_access_token(
        data={
            "sub": str(user_id),
            "role": role,
        }
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        role=role,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    email = payload.email.lower().strip()
    password = payload.password

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, password_hash, role
            FROM users
            WHERE email = %s
            """,
            (email,),
        )
        user = cur.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

    token = create_access_token(
        data={
            "sub": str(user["id"]),
            "role": user["role"],
        }
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        role=user["role"],
    )
