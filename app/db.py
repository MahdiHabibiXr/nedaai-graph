import aiosqlite
import msgs

DB_NAME = "sessions/nedaai.db"


async def create_users_table():
    # Connect to SQLite database (or create it if it doesn't exist)
    async with aiosqlite.connect(DB_NAME) as conn:
        # Create the 'users' table
        await conn.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incremented primary key
            chat_id INTEGER,                -- Telegram's unique user ID
            username TEXT,                         -- Optional Telegram username
            credits INTEGER DEFAULT 0,            -- Remaining free credits
            audio TEXT,                            -- Path or URL of the latest audio file
            gender TEXT,
            refs INTEGER DEFAULT 0,               -- Number of invitations
            model_name TEXT,
            duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- User creation timestamp
        );
        """
        )
        await conn.commit()

    print("Users table created successfully.")


async def create_generations_table():
    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute(
            """
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incremented primary key
            chat_id INTEGER,                       -- Telegram's unique user ID
            audio TEXT,                            -- Input text for generation
            model_name TEXT,                            -- Model used for generation
            duration INTEGER,                      -- Duration of the generated audio
            replicate_id INTEGER,                 -- ID of the original generation
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Generation creation timestamp
        );
        """
        )
        await conn.commit()

    print("Generations table created successfully.")


async def create_uvr_generations():
    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute(
            """
        CREATE TABLE IF NOT EXISTS uvrs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incremented primary key
            chat_id INTEGER,                       -- Telegram's unique user ID
            audio TEXT,                            -- Input text for generation
            vocal TEXT NULL,                       -- vocals output
            instrument TEXT NULL,                  -- instruments output
            duration INTEGER,                      -- Duration of the generated audio
            replicate_id INTEGER,                  -- ID of the original generation
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Generation creation timestamp
        );
        """
        )
        await conn.commit()

    print("Generations table created successfully.")


async def add_generation(chat_id, audio, model, duartion, replicate_id):
    # Check if user exists, if not create new user
    if not await user_exists(chat_id):
        await create_user(chat_id)

    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute(
            """
            INSERT INTO generations (chat_id, audio, model_name, duration, replicate_id) 
            VALUES (?, ?, ?, ?, ?)
        """,
            (chat_id, audio, model, duartion, replicate_id),
        )
        await conn.commit()


async def add_uvr_generation(chat_id, audio, duartion, replicate_id):
    # Check if user exists, if not create new user
    if not await user_exists(chat_id):
        await create_user(chat_id)

    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute(
            """
            INSERT INTO uvrs (chat_id, audio, duration, replicate_id) 
            VALUES (?, ?, ?, ?)
        """,
            (chat_id, audio, duartion, replicate_id),
        )
        await conn.commit()


async def update_uvr_column(chat_id, column, value, increment=False):
    """
    Update a specific column for a user in the 'users' table.

    Args:
        chat_id (int): The chat_id of the user to update.
        column (str): The column to update.
        value: The value to set or increment the column by.
        increment (bool): If True, increments the column value; otherwise, sets it.
    """
    # Check if user exists, if not create new user
    if not await user_exists(chat_id):
        await create_user(chat_id)

    async with aiosqlite.connect(DB_NAME) as conn:
        if increment:
            # Increment the column value
            query = f"UPDATE uvrs SET {column} = {column} + ? WHERE chat_id = ?"
        else:
            # Set the column value
            query = f"UPDATE uvrs SET {column} = ? WHERE chat_id = ?"

        await conn.execute(query, (value, chat_id))
        await conn.commit()


async def user_exists(chat_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.execute(
            "SELECT id FROM users WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def create_user(chat_id, username=None):
    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute(
            """
            INSERT INTO users (chat_id, username, credits) 
            VALUES (?, ?, ?)
        """,
            (chat_id, username, msgs.initial_gift),
        )
        await conn.commit()


async def update_user_column(chat_id, column, value, increment=False):
    """
    Update a specific column for a user in the 'users' table.

    Args:
        chat_id (int): The chat_id of the user to update.
        column (str): The column to update.
        value: The value to set or increment the column by.
        increment (bool): If True, increments the column value; otherwise, sets it.
    """
    # Check if user exists, if not create new user
    if not await user_exists(chat_id):
        await create_user(chat_id)

    async with aiosqlite.connect(DB_NAME) as conn:
        if increment:
            # Increment the column value
            query = f"UPDATE users SET {column} = {column} + ? WHERE chat_id = ?"
        else:
            # Set the column value
            query = f"UPDATE users SET {column} = ? WHERE chat_id = ?"

        await conn.execute(query, (value, chat_id))
        await conn.commit()


async def run_sql(sql_command):
    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.execute(sql_command) as cursor:
                result = await cursor.fetchall()
                await conn.commit()
                return result
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return None


async def get_users_columns(chat_id, columns):
    """
    Retrieve values from specific column(s) in the 'users' table for a given chat_id.

    Args:
        chat_id (int): The chat ID of the user.
        columns (list or str): Column name(s) to retrieve. Can be a single column or a list of columns.

    Returns:
        dict or None: A dictionary of column-value pairs if the user exists, otherwise None.
    """
    # Ensure columns is a list to handle both single and multiple columns
    if isinstance(columns, str):
        columns = [columns]

    # Convert columns list to a comma-separated string for the SQL query
    columns_str = ", ".join(columns)

    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            query = f"SELECT {columns_str} FROM users WHERE chat_id = ?"
            async with conn.execute(query, (chat_id,)) as cursor:
                result = await cursor.fetchone()

                if result:
                    return dict(
                        zip(columns, result)
                    )  # Map columns to their corresponding values
                else:
                    return None  # User not found
    except aiosqlite.Error as e:
        print(f"Database error: {e}")
        return None


async def add_status_column_to_users():
    """
    Add a 'status' column to the 'users' table if it doesn't already exist.
    """
    async with aiosqlite.connect(DB_NAME) as conn:
        # Check if the 'gender' column already exists
        async with conn.execute("PRAGMA table_info(users)") as cursor:
            columns = [column[1] async for column in cursor]
            if "status" not in columns:
                # Add the 'status' column
                await conn.execute("ALTER TABLE users ADD COLUMN status TEXT")
                await conn.commit()
                print("Status column added to users table.")
            else:
                print("Status column already exists in users table.")


async def generate_users_report():
    """
    Generate a report about the users in the 'users' table.

    Returns:
        str: A formatted string report about the users.
    """
    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.execute("SELECT COUNT(*) FROM users") as cursor:
                total_users = (await cursor.fetchone())[0]

            if total_users == 0:
                return "No users found in the database."

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE credits = 120"
            ) as cursor:
                credits_120 = (await cursor.fetchone())[0]

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE credits <= 120 AND credits > 100"
            ) as cursor:
                credits_120_100 = (await cursor.fetchone())[0]

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE credits <= 100 AND credits > 50"
            ) as cursor:
                credits_100_50 = (await cursor.fetchone())[0]

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE credits <= 50 AND credits > 25"
            ) as cursor:
                credits_50_25 = (await cursor.fetchone())[0]

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE credits <= 25 AND credits >= 0"
            ) as cursor:
                credits_25_0 = (await cursor.fetchone())[0]

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE audio IS NOT NULL"
            ) as cursor:
                audio_not_none = (await cursor.fetchone())[0]

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE refs > 0"
            ) as cursor:
                refs_greater_than_0 = (await cursor.fetchone())[0]

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE gender = 'male'"
            ) as cursor:
                male_users = (await cursor.fetchone())[0]

            async with conn.execute(
                "SELECT COUNT(*) FROM users WHERE gender = 'female'"
            ) as cursor:
                female_users = (await cursor.fetchone())[0]

            report_lines = [
                "📊 **Users Report:**\n",
                f"👥 **Total:** {total_users}\n",
                f"💳 **Credits = 120:** {credits_120} ({credits_120 / total_users * 100:.2f}%)",
                f"💳 **Credits 120-100:** {credits_120_100} ({credits_120_100 / total_users * 100:.2f}%)",
                f"💳 **Credits 100-50:** {credits_100_50} ({credits_100_50 / total_users * 100:.2f}%)",
                f"💳 **Credits 50-25:** {credits_50_25} ({credits_50_25 / total_users * 100:.2f}%)",
                f"💳 **Credits 25-0:** {credits_25_0} ({credits_25_0 / total_users * 100:.2f}%)\n",
                f"🎧 **Audio not none:** {audio_not_none} ({audio_not_none / total_users * 100:.2f}%)\n",
                f"🔗 **Refs > 0:** {refs_greater_than_0} ({refs_greater_than_0 / total_users * 100:.2f}%)\n",
                f"♂️ **Male:** {male_users} ({male_users / total_users * 100:.2f}%)",
                f"♀️ **Female:** {female_users} ({female_users / total_users * 100:.2f}%)",
            ]

            return "\n".join(report_lines)
    except aiosqlite.Error as e:
        return f"Database error: {e}"


async def generate_generations_report():
    """
    Generate a report about the generations in the 'generations' table.

    Returns:
        str: A formatted string report about the generations.
    """
    try:
        async with aiosqlite.connect(DB_NAME) as conn:
            async with conn.execute("SELECT COUNT(*) FROM generations") as cursor:
                total_generations = (await cursor.fetchone())[0]

            if total_generations == 0:
                return "No generations found."

            async with conn.execute("SELECT SUM(duration) FROM generations") as cursor:
                total_duration = (await cursor.fetchone())[0] or 0

            async with conn.execute(
                "SELECT COUNT(DISTINCT chat_id) FROM generations"
            ) as cursor:
                unique_users = (await cursor.fetchone())[0]

            average_duration_per_user = (
                total_duration / unique_users if unique_users else 0
            )

            async with conn.execute(
                "SELECT model_name, COUNT(*), SUM(duration) FROM generations GROUP BY model_name ORDER BY COUNT(*) DESC"
            ) as cursor:
                model_stats = await cursor.fetchall()

            report_lines = [
                "📊 **Generations Report:**\n",
                f"🔢 **Total:** {total_generations}",
                f"⏳ **Duration:** {total_duration} sec",
                f"👥 **Users:** {unique_users}",
                f"📈 **Avg/User:** {average_duration_per_user:.2f} sec",
                f"🛠️ **Models:** {len(model_stats)}\n",
            ]

            for rank, (model_name, count, duration) in enumerate(model_stats, start=1):
                percentage = (count / total_generations) * 100
                report_lines.append(
                    f"{rank}. **{model_name}:** {percentage:.2f}%, {count} generations, {duration} sec"
                )

            return "\n".join(report_lines)
    except aiosqlite.Error as e:
        return f"Database error: {e}"
