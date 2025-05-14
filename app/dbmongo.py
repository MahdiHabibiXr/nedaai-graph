from beanie import Document, init_beanie
from pydantic import Field
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, UTC, timedelta
from enum import Enum
from typing import Optional
import uuid
import msgs
import os
from pymongo import DESCENDING
import logfire

# configure logfire
logfire.configure(token="pylf_v1_us_twTVZHLXCZzLwrCJ292l3y5cgrsgN4t6DYfyCyTcMpWb")


class Status(str, Enum):
    init = "init"
    inqueue = "inqueue"
    processing = "processing"
    done = "done"
    error = "error"


class GenerationType(str, Enum):
    vocal_remover = "vocal_remover"
    voice_clone = "voice_clone"


class Gender(str, Enum):
    male = "male"
    female = "female"
    idontfuckingknow = "none"


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    expired = "expired"


# Beanie Models
class User(Document):
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4, json_schema_extra={"index": True, "unique": True}
    )
    chat_id: int
    username: Optional[str]
    credits: float = msgs.initial_gift
    refs: Optional[list[int]] = []
    paid: bool = False
    created_at: datetime = datetime.now()
    phone: Optional[str] = ""

    class Settings:
        name = "users"


class Generation(Document):
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4, json_schema_extra={"index": True, "unique": True}
    )
    chat_id: int
    input_url: Optional[str]
    output_url: Optional[list[str]]
    model_name: Optional[str]
    duration: float
    replicate_id: Optional[str]
    process_time: Optional[float] = 0
    status: Status = Status.init
    created_at: datetime = datetime.now(UTC)
    gentype: Optional[GenerationType]
    gender: Optional[Gender] = Gender.idontfuckingknow
    paid: bool
    cost: Optional[float]
    pitch: Optional[int] = None
    model_url: Optional[str] = None

    class Settings:
        name = "generations"
        indexes = [
            [("created_at", -1)],
            [("chat_id", 1), ("created_at", -1)],
        ]


class Payment(Document):
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4, json_schema_extra={"index": True, "unique": True}
    )
    chat_id: int
    amount: int
    status: PaymentStatus = PaymentStatus.pending
    package_seconds: int  # Amount of seconds to be added after payment
    payment_link: Optional[str]
    transaction_id: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None

    class Settings:
        name = "payments"
        indexes = [
            [("created_at", -1)],
            [("chat_id", 1), ("created_at", -1)],
            [("status", 1)],
        ]


# Database initialization
async def init_db():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    await init_beanie(
        database=client.nedaai, document_models=[User, Generation, Payment]
    )


# User operations
async def create_user(chat_id: int, username: Optional[str] = None) -> None:
    """Creates a new user if they do not already exist."""
    if not await user_exists(chat_id):
        user = User(chat_id=chat_id, username=username)
        await user.insert()
        print("User created:", chat_id)
        logfire.info(f"User created: {chat_id}")


async def user_exists(chat_id: int) -> bool:
    """Checks if a user exists."""
    return await User.find_one(User.chat_id == chat_id) is not None


async def find_user(chat_id: int) -> User | None:
    return await User.find_one(User.chat_id == chat_id)


async def add_generation(
    chat_id: int,
    input_url: Optional[str] = None,
    output_url: Optional[list[str]] = None,
    model_name: Optional[str] = None,
    duration: float = 0.0,
    replicate_id: Optional[str] = None,
    process_time: Optional[float] = None,
    status: Status = Status.init,
    gentype: Optional[GenerationType] = None,
    gender: Optional[Gender] = Gender.idontfuckingknow,
    paid: bool = False,
    cost: Optional[float] = None,
    pitch: Optional[int] = None,
    model_url: Optional[str] = None,
) -> None:
    """Adds a new generation."""
    generation = Generation(
        chat_id=chat_id,
        input_url=input_url,
        output_url=output_url,
        model_name=model_name,
        duration=duration,
        replicate_id=replicate_id,
        process_time=process_time,
        status=status,
        created_at=datetime.now(UTC),
        gentype=gentype,
        gender=gender,
        paid=paid,
        cost=cost,
        pitch=pitch,
        model_url=model_url,
    )
    await generation.insert()  # Ensure this is awaited
    print("Generation added:", chat_id)
    logfire.info(f"Generations added: {chat_id}")


async def update_user_column(
    chat_id: int, column: str, value: any, increment: bool = False
) -> None:
    """Updates a specific user field."""
    if not await user_exists(chat_id):
        await create_user(chat_id)

    user = await User.find_one(User.chat_id == chat_id)
    if increment:
        current_value = getattr(user, column, 0)
        setattr(user, column, current_value + value)
    else:
        setattr(user, column, value)
    await user.save()

    print(f"User {chat_id} updated: {column} -> {value}")
    logfire.info(f"User {chat_id} updated: {column} -> {value}")


async def add_ref_to_user(chat_id: int, ref_chat_id: int) -> None:
    """Appends a chat_id to the user's refs list."""
    if not await user_exists(chat_id):
        return

    user = await find_user(chat_id=chat_id)
    # if not user:
    #     return
    # if user.get("refs") is None:
    #     user.refs = []
    user.refs.append(ref_chat_id)

    await user.save()
    print(f"User {chat_id} updated: added ref {ref_chat_id}")
    logfire.info(f"User {chat_id} updated: added ref {ref_chat_id}")


async def user_is_paid(chat_id: int) -> bool:
    user = await find_user(chat_id)
    return user.paid


async def get_users_columns(chat_id: int, columns: list) -> dict:
    """Retrieves specific user fields."""
    user = await User.find_one({"chat_id": chat_id})
    if not user:
        raise ValueError("User does not exist")

    if isinstance(columns, str):
        columns = [columns]
    return {column: getattr(user, column) for column in columns}


async def update_generation_column(
    generation_id: str, column: str, value: any, increment: bool = False
) -> None:
    """Updates a specific generation field."""
    generation = await Generation.find_one({"uid": generation_id})
    if not generation:
        raise ValueError("Generation does not exist")

    if increment:
        current_value = getattr(generation, column, 0)
        setattr(generation, column, current_value + value)
    else:
        setattr(generation, column, value)

    await generation.save()
    print(f"Generation {generation_id} updated: {column} -> {value}")
    logfire.info(f"Generation {generation_id} updated: {column} -> {value}")


async def update_generations_columns(generation_id: str, updates: dict) -> None:
    """
    Updates multiple fields in a generation document in the database.

    Args:
        generation_id (str): The unique identifier of the generation document to update.
        updates (dict): A dictionary containing field names as keys and the corresponding new values.

        await update_generations_columns("12345", {"status": "completed", "duration": 120})

    This will update the "status" and "duration" fields of the generation document with ID "12345".
    """
    generation = await Generation.find_one({"uid": generation_id})
    if not generation:
        raise ValueError("Generation does not exist")

    for column, value in updates.items():
        setattr(generation, column, value)

    await generation.save()
    print(f"Generation {generation_id} updated with: {updates}")
    logfire.info(f"Generation {generation_id} updated with: {updates}")


async def get_last_generation_by_chat_id(chat_id: int) -> Optional[Generation]:
    """Retrieves the last generation for a given chat_id."""
    generation = (
        await Generation.find(Generation.chat_id == chat_id)
        .sort([("-created_at", DESCENDING), ("_id", DESCENDING)])
        .first_or_none()
    )
    return generation


async def count_queue_items() -> int:
    """
    Count all generations with status 'inqueue'.

    Returns:
        Number of generations in queue
    """
    return await Generation.find(Generation.status == Status.inqueue).count()


async def generate_users_report() -> str:
    """Generates a statistical report of users."""
    # Get total users count
    total_users = await User.find_all().count()

    if total_users == 0:
        return "No users found in the database."

    # Calculate credit ranges
    credits_ranges = {
        "120": await User.find({"credits": 120}).count(),
        "120-100": await User.find({"credits": {"$lte": 120, "$gt": 100}}).count(),
        "100-50": await User.find({"credits": {"$lte": 100, "$gt": 50}}).count(),
        "50-25": await User.find({"credits": {"$lte": 50, "$gt": 25}}).count(),
        "25-0": await User.find({"credits": {"$lte": 25, "$gte": 0}}).count(),
    }

    # Count users with refs
    refs_greater_than_0 = await User.find(
        {"refs": {"$exists": True, "$ne": []}}
    ).count()

    # Count users by gender
    male_users = await User.find({"gender": "male"}).count()
    female_users = await User.find({"gender": "female"}).count()

    # Generate report
    report_lines = [
        "📊 **Users Report:**\n",
        f"👥 **Total:** {total_users}\n",
    ]

    # Add credit ranges to report
    for range_name, count in credits_ranges.items():
        percentage = (count / total_users * 100) if total_users > 0 else 0
        report_lines.append(f"💳 **Credits {range_name}:** {count} ({percentage:.2f}%)")

    # Add refs and gender stats
    report_lines.extend(
        [
            f"\n🔗 **Refs > 0:** {refs_greater_than_0} ({(refs_greater_than_0 / total_users * 100) if total_users > 0 else 0:.2f}%)\n",
            f"♂️ **Male:** {male_users} ({(male_users / total_users * 100) if total_users > 0 else 0:.2f}%)",
            f"♀️ **Female:** {female_users} ({(female_users / total_users * 100) if total_users > 0 else 0:.2f}%)",
        ]
    )

    return "\n".join(report_lines)


async def generate_generations_report() -> str:
    """Generates a statistical report of generations."""
    # Get total generations count
    total_generations = await Generation.find_all().count()

    if total_generations == 0:
        return "No generations found."

    # Calculate total duration
    duration_result = (
        await Generation.find_all()
        .aggregate([{"$group": {"_id": None, "total_duration": {"$sum": "$duration"}}}])
        .to_list(length=1)
    )

    total_duration = duration_result[0]["total_duration"] if duration_result else 0

    # Get unique users count
    unique_users = len(await Generation.distinct("chat_id"))

    # Get model statistics
    model_stats = (
        await Generation.find_all()
        .aggregate(
            [
                {
                    "$group": {
                        "_id": "$model_name",
                        "count": {"$sum": 1},
                        "total_duration": {"$sum": "$duration"},
                    }
                },
                {"$sort": {"count": -1}},
            ]
        )
        .to_list(length=None)
    )

    # Generate report
    report_lines = [
        "📊 **Generations Report:**\n",
        f"🔢 **Total:** {total_generations}",
        f"⏳ **Duration:** {total_duration:.1f} sec",
        f"👥 **Users:** {unique_users}",
    ]

    # Add model statistics
    for model in model_stats:
        if model["_id"]:  # Skip if model name is None
            percentage = model["count"] / total_generations * 100
            report_lines.append(
                f"🗣️ **{model['_id']}:** {model['count']} times ({percentage:.2f}%), {model['total_duration']:.1f} sec"
            )

    return "\n".join(report_lines)


# Payment operations
async def create_payment(chat_id: int, amount: int, package_seconds: int) -> Payment:
    """Creates a new payment record"""
    payment = Payment(chat_id=chat_id, amount=amount, package_seconds=package_seconds)
    await payment.insert()
    logfire.info(
        f"Payment created: {chat_id}, amount: {amount}, seconds: {package_seconds}"
    )
    return payment


async def complete_payment(payment_uid: uuid.UUID, transaction_id: str) -> None:
    """Marks a payment as completed and updates user credits"""
    payment = await Payment.find_one(Payment.uid == payment_uid)
    if not payment:
        raise ValueError("Payment not found")

    payment.status = PaymentStatus.completed
    payment.transaction_id = transaction_id
    payment.completed_at = datetime.now(UTC)
    await payment.save()

    # Update user credits
    user = await find_user(payment.chat_id)
    if user:
        user.credits += payment.package_seconds
        user.paid = True
        await user.save()

    logfire.info(
        f"Payment completed: {payment_uid}, user: {payment.chat_id}, amount: {payment.amount}"
    )


async def get_pending_payment(chat_id: int) -> Optional[Payment]:
    """Gets the latest pending payment for a user"""
    return await Payment.find_one(
        {"chat_id": chat_id, "status": PaymentStatus.pending},
        sort=[("-created_at", DESCENDING)],
    )


async def expire_old_payments() -> int:
    """Expires payments that are older than 1 hour"""
    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
    result = await Payment.find(
        {"status": PaymentStatus.pending, "created_at": {"$lt": one_hour_ago}}
    ).update({"$set": {"status": PaymentStatus.expired}})

    count = result.modified_count if result else 0
    if count > 0:
        logfire.info(f"Expired {count} old payments")
    return count
