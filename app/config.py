# import os
# import asyncio
# from db import create_users_table, DB_NAME, create_generations_table

# path = "sessions"

# # Create sessions directory if it doesn't exist
# if not os.path.exists(path):
#     os.makedirs(path)
#     print(f"{path} Directory created.")
# else:
#     print(f"{path} Directory already exists.")

# # Create db file if it doesn't exist
# if not os.path.exists(DB_NAME):
#     create_users_table()
#     print(f"Database {DB_NAME} created.")
# else:
#     print(f"{DB_NAME} Database already exists.")


# # Create generations table if it doesn't exist
# async def run_generation():
#     await create_generations_table()
