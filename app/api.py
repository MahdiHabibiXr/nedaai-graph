from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
import os
import shutil
from pathlib import Path
from dbmongo import (
    init_db,
    update_user_column,
    update_generation_column,
    update_generations_columns,
    User,
    Generation,
    Status,
    Gender,
    GenerationType,
)
from fastapi.middleware.cors import CORSMiddleware
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="Nedaai API",
    description="An API for voice cloning and vocal removing tasks",
    version="1.0.0",
)

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    await init_db()


class UserUpdate(BaseModel):
    chat_id: int
    column: str
    value: any
    increment: bool = False


class GenerationUpdate(BaseModel):
    generation_id: str
    updates: dict



@app.post("/db/update-user")
async def update_user(update_data: UserUpdate):
    """
    Update a user's column in the database
    """
    try:
        await update_user_column(
            update_data.chat_id,
            update_data.column,
            update_data.value,
            update_data.increment
        )
        return {"status": "success", "message": "User updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/db/update-generation")
async def update_generation(update_data: GenerationUpdate):
    """
    Update multiple fields of a generation in the database
    """
    try:
        await update_generations_columns(
            update_data.generation_id,
            update_data.updates
        )
        return {"status": "success", "message": "Generation updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/db/user/{chat_id}")
async def get_user(chat_id: int):
    """
    Get user information by chat_id
    """
    try:
        user = await User.find_one(User.chat_id == chat_id)
        if user:
            return user.dict()
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/db/generation/{generation_id}")
async def get_generation(generation_id: str):
    """
    Get generation information by generation_id
    """
    try:
        generation = await Generation.find_one({"uid": uuid.UUID(generation_id)})
        if generation:
            return generation.dict()
        raise HTTPException(status_code=404, detail="Generation not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
