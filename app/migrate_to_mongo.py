import sqlite3
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone
import os
from dbmongo import User, Generation, GenerationType, Status, Gender, init_db
import uuid

# SQLite connection
sqlite_db_path = "sessions/nedaai.db"
sqlite_conn = sqlite3.connect(sqlite_db_path)
sqlite_cursor = sqlite_conn.cursor()


# Convert timestamp string to a proper datetime object
def convert_timestamp(timestamp):
    if not timestamp:
        return datetime.now(timezone.utc)
    try:
        # Attempt to parse the timestamp as a formatted string
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        try:
            # Fallback to parsing as a Unix timestamp
            return datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
        except ValueError:
            return datetime.now(timezone.utc)


async def migrate_users():
    sqlite_cursor.execute(
        "SELECT chat_id, username, credits, refs, created_at FROM users"
    )
    users = sqlite_cursor.fetchall()

    for user in users:
        chat_id, username, credits, refs, created_at = user

        # Convert refs to list if it exist
        user_data = User(
            uid=uuid.uuid4(),
            chat_id=chat_id,
            username=username,
            credits=credits or 0,
            refs=[],
            created_at=convert_timestamp(created_at),
            paid=False,  # Default value for existing users
        )
        await user_data.insert()
    print("✅ Users migrated successfully!")


async def migrate_generations():
    sqlite_cursor.execute(
        "SELECT chat_id, audio, model_name, duration, replicate_id, created_at FROM generations"
    )
    generations = sqlite_cursor.fetchall()

    for gen in generations:
        chat_id, audio, model_name, duration, replicate_id, created_at = gen

        gen_data = Generation(
            uid=uuid.uuid4(),
            chat_id=chat_id,
            input_url=audio,  # Previous audio field maps to input_url
            output_url=[],  # Default empty list for output_url
            model_name=model_name,
            duration=float(duration) if duration else 0.0,
            replicate_id=replicate_id,
            status=Status.done,  # Assuming completed generations
            created_at=convert_timestamp(created_at),
            gentype=GenerationType.voice_clone,  # Default for existing voice generations
            paid=False,  # Default value for existing generations
            gender=Gender.idontfuckingknow,
            cost=0,  # Default value for existing generations
        )
        await gen_data.insert()
    print("✅ Generations migrated successfully!")


async def migrate_uvr_generations():
    sqlite_cursor.execute(
        "SELECT chat_id, audio, vocal, instrument, duration, replicate_id, created_at FROM uvrs"
    )
    uvrs = sqlite_cursor.fetchall()

    for uvr in uvrs:
        chat_id, audio, vocal, instrument, duration, replicate_id, created_at = uvr

        # For UVR, we'll store both vocal and instrument URLs in output_url
        output_urls = []
        if vocal:
            output_urls.append(vocal)
        if instrument:
            output_urls.append(instrument)

        gen_data = Generation(
            uid=uuid.uuid4(),
            chat_id=chat_id,
            input_url=audio,
            output_url=output_urls,
            model_name="vocal_remover",
            duration=float(duration) if duration else 0.0,
            replicate_id=replicate_id,
            status=Status.done,
            created_at=convert_timestamp(created_at),
            gentype=GenerationType.vocal_remover,
            paid=False,
            cost=0,
        )
        await gen_data.insert()
    print("✅ UVR Generations migrated successfully!")


async def main():
    # Initialize MongoDB connection
    await init_db()

    # Run migrations
    await migrate_users()
    await migrate_generations()
    await migrate_uvr_generations()

    # Close SQLite connection
    sqlite_conn.close()

    print("🎉 Migration completed!")


if __name__ == "__main__":
    asyncio.run(main())
