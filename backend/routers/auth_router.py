# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
from typing import Optional

from database import get_session
from models import User, UserRole # Импортируем UserRole
from schemas import UserCreate, UserRead, Token, UserUpdate
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # ИСПРАВЛЕНИЕ: Жестко задаем роль CLIENT, игнорируя то, что пришло в JSON
    db_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=UserRole.CLIENT 
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# НОВОЕ (по ТЗ): Получение своего профиля
@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

# НОВОЕ (по ТЗ): Редактирование профиля клиента
@router.patch("/me", response_model=UserRead)
def update_my_profile(
    user_data: UserUpdate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user_data.full_name:
        current_user.full_name = user_data.full_name
    if user_data.phone:
        current_user.phone = user_data.phone
    if user_data.password:
        current_user.hashed_password = get_password_hash(user_data.password)
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user