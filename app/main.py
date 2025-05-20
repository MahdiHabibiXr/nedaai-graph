import json
import logging
import os

import dotenv
from pyrogram import Client, filters, idle
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
    CallbackQuery,
)

import payment
import msgs
import rvc
import uvr
import logfire

# configure logfire
logfire.configure(token="pylf_v1_us_twTVZHLXCZzLwrCJ292l3y5cgrsgN4t6DYfyCyTcMpWb")

# from db import (
#     create_user,
#     create_users_table,
#     get_users_columns,
#     update_user_column,
#     user_exists,
#     DB_NAME,
#     create_generations_table,
#     add_generation,
#     add_status_column_to_users,
#     generate_users_report,
#     generate_generations_report,
#     create_uvr_generations,
#     add_uvr_generation,
#     update_uvr_column,
#     run_sql,
# )

from dbmongo import (
    init_db,
    create_user,
    user_exists,
    add_generation,
    update_user_column,
    get_users_columns,
    generate_users_report,
    generate_generations_report,
    user_is_paid,
    get_last_generation_by_chat_id,
    update_generation_column,
    update_generations_columns,
    Status,
    GenerationType,
    Gender,
    add_ref_to_user,
    count_queue_items,
)

from uploader import upload_file, tapsage_upload
from asyncio import Semaphore

dotenv.load_dotenv(".env")


links = msgs.channels_list
MODELS_DIR = "sessions/models.json"
CORES = 5
semaphore = Semaphore(CORES)

bot = Client(
    "sessions/nedaai",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("TOKEN"),
)

# initialize the tables
# create_users_table()
# create_generations_table()
# add_gender_column_to_users()
# create_uvr_generations()
# add_status_column_to_users()


async def is_joined(app: Client, user_id):
    not_joined = []
    for channel in links:
        try:
            await app.get_chat_member(channel, user_id)
        except:  # noqa: E722
            not_joined.append(channel)
    return not_joined


# @bot.on_message(filters.user(msgs.bot_id))
# async def handle_bot_prompts(client, message):

#     print(message)


@bot.on_message(filters.user(msgs.admin_id) & filters.document)
async def handle_file(client, message: Message):
    logging.basicConfig(level=logging.INFO)
    print(message.document)

    try:
        file = await message.download(f"./{MODELS_DIR}")
        await message.reply(file)
        await message.reply("Json saved successfully")
        logging.basicConfig(level=logging.INFO)
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        await message.reply(f"Error saving json file: {str(e)}")


@bot.on_message(filters.user(msgs.admin_id) & (filters.reply))
async def handle_reply(client, message: Message):
    reply = message.reply_to_message

    if reply.voice or reply.audio:
        await message.reply(reply.voice.file_id or reply.audio.file_id)
    elif reply.text:
        await message.reply(reply.text)
    elif reply.document:
        await message.reply(reply.document.file_)
    elif reply.photo:
        await message.reply(reply.photo.file_id)
    elif reply.video:
        await message.reply(reply.video.file_)


# @bot.on_message(filters.user(msgs.admin_id) & filters.forwarded)
# async def handle_forward(client, message: Message):
#     await message.reply(message.forward_from.id)


@bot.on_message(filters.user(msgs.admin_id) & filters.regex("/admin"))
async def amdin(client: Client, message: Message):
    text = message.text
    message.from_user.mention

    if ("/get_credits ") in text:
        user_id = text.replace("/admin/get_credits ", "").strip()

        if await user_exists(int(user_id)):
            user_data = await get_users_columns(
                int(user_id), ["credits", "paid", "username"]
            )
            credits = user_data["credits"]
            paid = user_data["paid"]
            username = user_data["username"]
            await message.reply(
                f"User {user_id} has {credits} credits\npaid : {paid}\nusername: @{username}"
            )
        else:
            await message.reply(f"User {user_id} does not exist")

    #     elif ("/exec_120") in text:
    #         command = """UPDATE users
    # SET credits = 60
    # WHERE chat_id IN (SELECT chat_id FROM users WHERE credits > 60 AND credits <= 120);
    # """
    #         await run_sql(command)
    #         await message.reply("Executed successfully")

    # elif ("/config") in text:
    #     await init_db()
    #     await message.reply("Database created successfully")

    elif ("/get_db") in text:
        await client.send_document(message.chat.id, "sessions/nedaai.db")

    elif ("/create_payment") in text:
        # text = text.replace("/admin/create_payment", "")
        amount = text.split(" ")[1]
        description = text.split(" ")[2]

        payment_id = await payment.create_payping_payment(
            amount, description=description
        )

        link = (
            f"https://wallet.pixiee.io/api/v1/apps/payping/purchases/{payment_id}/start"
        )

        await message.reply(
            f"Payment created successfully: `{payment_id}`\n\n{link}\n\n`/admin/get_payment_status {payment_id}`"
        )
        logfire.info(f"Payment created successfully: {payment_id}")

    elif ("/get_payment_status") in text:
        payment_id = text.split(" ")[1]
        status = await payment.get_payment_status(payment_id)

        await message.reply(f"```json\n{status}\n```")

    elif ("set_banner_image") in text:
        banner_img_id = text.replace("/admin/set_banner_image", "")
        msgs.banner_img_id = banner_img_id

        await message.reply(msgs.banner_img_id)
        # await client.send_photo(msgs.admin_id, int(banner_img_id))

    elif ("/add_credits") in text:
        text = text.replace("/admin/add_credits", "").split(" ")
        user_chat_id = int(text[1])
        amount = int(text[2])

        if await user_exists(user_chat_id):
            await update_user_column(user_chat_id, "credits", amount, increment=True)
            await update_user_column(user_chat_id, "paid", True)

            new_credits = (await get_users_columns(user_chat_id, "credits"))["credits"]

            await message.reply(
                f"added {amount} credits to {user_chat_id} user credits updated. User is now a paid user"
            )
            await client.send_message(
                user_chat_id,
                msgs.added_credits.format(credits=amount, new_credits=new_credits),
            )
        else:
            await message.reply(f"user {user_chat_id} does not exists")

    elif ("/set_credits") in text:
        text = text.replace("/admin/set_credits", "").split(" ")
        user_chat_id = int(text[1])
        amount = int(text[2])

        if await user_exists(user_chat_id):
            await update_user_column(user_chat_id, "credits", amount, increment=False)
            new_credits = (await get_users_columns(user_chat_id, "credits"))["credits"]

            await message.reply(
                f"set {amount} credits to {user_chat_id} user credits updated"
            )

        else:
            await message.reply(f"user {user_chat_id} does not exist")

    elif ("/report") in text:
        users_report = await generate_users_report()
        gens_report = await generate_generations_report()

        await message.reply(users_report)
        await message.reply(gens_report)


@bot.on_message(filters.chat(msgs.admin_id) & filters.bot)
async def handle_bot_prompts(client: Client, message: Message):
    print(message.text)
    # if message.from_user.id == msgs.bot_id:


@bot.on_message((filters.regex("/start") | filters.regex("/Start")) & filters.private)
async def start_text(client: Client, message: Message):
    not_joined_channels = await is_joined(bot, message.from_user.id)
    chat_id = message.chat.id
    message.from_user.mention
    username = message.from_user.username

    # check if user exists
    if not await user_exists(chat_id):
        await create_user(chat_id, username)
        await message.reply(msgs.gift_msg.format(inital_credits=msgs.initial_gift))
        # Check if user is invited, if yes add reward credits to inviter
        if len(message.text.split(" ")) == 2:
            invited_by = int(message.text.split(" ")[1])
            # await update_user_column(invited_by, "refs", chat_id)
            await add_ref_to_user(invited_by, chat_id)

            await client.send_message(
                invited_by,
                msgs.invite_successfully.format(
                    user=username,
                    gift_credits=msgs.invitation_gift,
                    admin=msgs.admin_username,
                ),
            )

            await update_user_column(invited_by, "credits", msgs.invitation_gift, True)

    # Check if user has joined required channels
    if not_joined_channels:
        buttons = joined_channels_button(not_joined_channels)
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(msgs.join_channels, reply_markup=reply_markup)

    else:
        await message.reply(msgs.start.format(username=username))


@bot.on_message(filters.private & (filters.voice | filters.audio))
async def get_voice_or_audio(client: Client, message: Message):
    if not await user_exists(message.chat.id):
        await message.reply(msgs.user_not_exists)
        return

    if message.from_user.is_bot:
        return None

    # if not await user_exists(message.chat.id):
    #     await create_user(message.chat.id, message.from_user.username)
    #     await message.reply(msgs.gift_msg.format(inital_credits=msgs.initial_gift))

    not_joined_channels = await is_joined(bot, message.from_user.id)

    # Check if user has joined required channels
    if not_joined_channels:
        buttons = joined_channels_button(not_joined_channels)
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(msgs.join_channels, reply_markup=reply_markup)
        return

    t_id = message.chat.id
    media = message.voice or message.audio
    duration = media.duration

    mes = await message.reply(msgs.uploading_file)

    credits = await get_users_columns(t_id, ["credits"])

    generatin = await get_last_generation_by_chat_id(t_id)

    try:
        # check if user is not paid
        if not await user_is_paid(t_id):
            if generatin is not None and (
                generatin.status == Status.inqueue
                or generatin.status == Status.processing
            ):
                await mes.delete()

                await message.reply(msgs.already_inqueue)

                return

            # check the duration limit of audio
            if duration >= msgs.convert_limit:
                # check if user hs at least enough credits for vocal remover task
                if duration / 2 <= credits["credits"]:
                    # check if user if not bot
                    if media and not message.from_user.is_bot:
                        async with semaphore:
                            # save file
                            file_id = media.file_id
                            file_name = f"files/{t_id}/voice.ogg"

                            await client.download_media(file_id, file_name=file_name)

                            await add_generation(t_id, duration=duration, paid=False)

                            await mes.delete()

                            # ask user the task
                            buttons = create_reply_markup(msgs.task_btns)
                            await message.reply(msgs.task_msg, reply_markup=buttons)

                else:
                    await mes.delete()
                    await message.reply(msgs.no_credits)

            else:
                await mes.delete()
                await message.reply(msgs.short_audio.format(limit=msgs.convert_limit))

        # user is paid
        else:
            if media is not None:
                # check time limitation for paid users
                if duration >= msgs.convert_limit_paid:
                    file_name = f"files/{t_id}/voice.ogg"

                    await client.download_media(media.file_id, file_name=file_name)
                    await add_generation(t_id, duration=duration, paid=True)

                    await mes.delete()

                    # ask user the task
                    buttons = create_reply_markup(msgs.task_btns)
                    await message.reply(msgs.task_msg, reply_markup=buttons)

                else:
                    await mes.delete()
                    await message.reply(
                        msgs.short_audio.format(limit=msgs.convert_limit_paid)
                    )
            else:
                await mes.delete()
                await message.reply(msgs.unknown_error)

    except Exception as e:
        logfire.error(e)
        logging.basicConfig(level=logging.warning)
        logging.warning(e)
        # await client.send_message(msgs.admin_id, f"Error: {str(e)}")


@bot.on_callback_query()
async def callbacks(client: Client, callback_query: CallbackQuery):
    try:
        message = callback_query.message
        data = callback_query.data
        chat_id = callback_query.from_user.id

        return_to_menu = create_reply_markup([msgs.return_to_menu_button])
        username = callback_query.from_user.mention

        if data.startswith("cat_"):
            await callback_query.answer(msgs.select_category)
            return

        await message.delete()

        if not await user_exists(message.chat.id):
            await message.reply(msgs.user_not_exists)
            return

        # selected the task
        if data.startswith("task_"):
            async with semaphore:
                task = data.replace("task_", "")

                file = f"files/{chat_id}/voice.ogg"
                
                try:
                    # file_url = await upload_file(
                    #     file, file_name=f"nedaai/{chat_id}/input_voice.ogg"
                    # )
                    file_url = await tapsage_upload(file)

                except Exception as e:
                    logfire.error(f"Upload error: {e}")
                    await message.reply("خطا در آپلود فایل. لطفا بعدا تلاش کنید.")
                    return

                # file_url = await tapsage_upload(file)

                # create the generation
                generation = await get_last_generation_by_chat_id(int(chat_id))
                # add audio_url and
                await update_generations_columns(
                    generation.uid,
                    {
                        "input_url": file_url,
                        "gentype": GenerationType.voice_clone
                        if task == "voice_changer"
                        else GenerationType.vocal_remover,
                    },
                )

                if task == "voice_changer":
                    # ask user the gender
                    buttons = create_reply_markup(msgs.gender_btns)
                    await message.reply(msgs.gender_select, reply_markup=buttons)

                # vocal remover disabled
                {
                    # elif task == "vocal_remover":
                    #     user_data = await get_users_columns(
                    #         chat_id, ["duration", "credits", "audio"]
                    #     )
                    #     credits = user_data["credits"]
                    #     duration = user_data["duration"]
                    #     audio = user_data["audio"]
                    #     price = duration / 2
                    #     # check for enough credits
                    #     if credits < price:
                    #         await message.reply(msgs.no_credits)
                    #         return
                    #     # check for not short audio
                    #     if duration <= msgs.vocal_remove_limit:
                    #         await message.reply(msgs.short_audio_for_vocal_remove)
                    #         return
                    #     # user has enough credits
                    #     else:
                    #         new_credits = credits - price
                    #         await update_user_column(chat_id, "credits", new_credits)
                    #         prediction = uvr.create_vocal_reomver_task(audio, chat_id, duration)
                    #         # await add_uvr_generation(chat_id, audio, duration, prediction)
                    #         await message.reply(msgs.proccessing_emojie)
                    #         await message.reply(
                    #             msgs.proccessing.format(used_credits=price, credits=new_credits)
                    #         )
                }

        # selected the voice models
        elif data.startswith("voice_"):
            model_name = data.replace("voice_", "")

            generation = await get_last_generation_by_chat_id(chat_id)
            await update_generation_column(generation.uid, "model_name", model_name)

            # check the gender of input and selected voice
            model_data = get_value_from_json(MODELS_DIR, model_name)
            model_gender = model_data["gender"]

            # if model_data["gender"] is Gender.male.value:
            #     model_gender = Gender.male
            # else:
            #     model_gender = Gender.female

            # user_data = await get_users_columns(chat_id, "gender")
            # user_data = get_users_columns(chat_id, "gender")
            user_gender = generation.gender.value

            pitch = 0
            # same gender for user input and selected model
            if user_gender == model_gender:
                buttons = create_reply_markup(msgs.pitch_btns)
                await message.reply(msgs.pitch_select, reply_markup=buttons)

            # different gender for model and input
            else:
                # male to female => 12
                if (user_gender == "male") and (model_gender == "female"):
                    pitch = 12

                # female to male => -12
                elif (user_gender == "female") and (model_gender == "male"):
                    pitch = -12

                await process_pitch_conversion(
                    chat_id, data=None, message=message, pitch_based_on_gender=pitch
                )

        # selected the gender
        elif data.startswith("gender_"):
            gender = data.replace("gender_", "")

            generation = await get_last_generation_by_chat_id(chat_id)
            await update_generation_column(generation.uid, "gender", gender)

            # generate the available models as buttons from models.json
            buttons = create_reply_markup(generate_model_list(MODELS_DIR))
            await message.reply(
                msgs.voice_select,
                reply_markup=buttons,
            )

        elif data == "invite":
            # Get user's current refs count
            user_data = await get_users_columns(chat_id, ["refs", "credits"])
            if user_data is None:
                return

            refs = len(user_data["refs"]) if user_data["refs"] else 0
            credits = user_data["credits"]

            # Create unique invite link
            bot_info = await client.get_me()
            invite_link = f"https://t.me/{bot_info.username}?start={chat_id}"
            caption = f"{msgs.banner_msg}\n\n{invite_link}"

            await client.send_photo(chat_id, msgs.banner_img_id, caption=caption)
            await message.reply(
                msgs.invite_help.format(
                    refs=refs,
                    invite_link=invite_link,
                    credits=credits,
                    invitation_gift=msgs.invitation_gift,
                ),
                reply_markup=return_to_menu,
            )

        elif data == "buy_credits":
            # Get user's current credits
            user_data = await get_users_columns(chat_id, "credits")
            if user_data is None:
                return

            credits = user_data["credits"]
            btns = create_reply_markup(msgs.go_to_shop_btn)
            await message.reply(
                msgs.buy_credits_message.format(credits=credits),
                reply_markup=btns,
            )

        elif data == "help":
            await message.reply(
                msgs.help_msg.format(admin_username=msgs.admin_username),
                reply_markup=return_to_menu,
            )

        elif data == "convert_voice":
            await message.reply(msgs.convert_msg, reply_markup=return_to_menu)

        elif data == "vocal_remover":
            await message.reply(msgs.vocal_remove_msg, reply_markup=return_to_menu)

        elif data == "menu":
            buttons = create_reply_markup(msgs.menu_btns)
            await message.reply(msgs.menu_msg, reply_markup=buttons)

        elif data == "joined_channels":
            not_joined_channels = await is_joined(bot, chat_id)

            # Check if user has joined required channels
            if not_joined_channels:
                buttons = joined_channels_button(not_joined_channels)
                reply_markup = InlineKeyboardMarkup(
                    joined_channels_button(not_joined_channels)
                )
                await message.reply(msgs.join_channels, reply_markup=reply_markup)

            else:
                await message.reply(msgs.start.format(username=username))

        elif data.startswith("pitch_"):
            # check if user has enough credits
            await process_pitch_conversion(chat_id, data, message)

        elif data.startswith("buy_") and not data == "buy_credits":
            amount_key = data.replace("buy_", "")
            await message.reply(amount_key)

        elif data == "list":
            if not await user_exists(message.chat.id):
                await message.reply(msgs.user_not_exists)
                return

            btns = create_reply_markup(msgs.voice_list_btn)

            await message.reply(
                msgs.list_msg,
                reply_markup=btns,
            )
    except Exception as e:
        logfire.error(e)
        logging.error(f"Error in callback: {str(e)}")
        logging.error(f"chat_id: {chat_id}, data: {data}")
        await client.send_message(
            msgs.admin_id,
            f"Error in callback: {str(e)}\nchat_id: {chat_id}, data: {data}",
        )
        await client.send_message(
            chat_id,
            "مشکلی رخ داده است لطفا دوباره امتحان کنید یا با پشتیبانی در ارتباط باشید @nedaaisupport",
        )


@bot.on_message(filters.command("invite"))
async def invite_command(client: Client, message: Message):
    if not await user_exists(message.chat.id):
        await message.reply(msgs.user_not_exists)
        return
    chat_id = message.from_user.id

    # Get user's current refs count
    user_data = await get_users_columns(chat_id, ["refs", "credits"])
    if user_data is None:
        return

    refs = len(user_data["refs"]) if user_data["refs"] else 0
    credits = user_data["credits"]

    # Create unique invite link
    bot_info = await client.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start={chat_id}"
    caption = f"{msgs.banner_msg}\n\n{invite_link}"

    await client.send_photo(chat_id, msgs.banner_img_id, caption=caption)

    return_to_menu = create_reply_markup([msgs.return_to_menu_button])
    await message.reply(
        msgs.invite_help.format(
            refs=refs,
            invite_link=invite_link,
            credits=credits,
            invitation_gift=msgs.invitation_gift,
        ),
        reply_markup=return_to_menu,
    )


@bot.on_message(filters.command("credits"))
async def credits_command(client: Client, message: Message):
    if not await user_exists(message.chat.id):
        await message.reply(msgs.user_not_exists)
        return
    chat_id = message.from_user.id

    # Get user's current credits
    user_data = await get_users_columns(chat_id, "credits")
    if user_data is None:
        return

    credits = user_data["credits"]
    return_to_menu = create_reply_markup([msgs.return_to_menu_button])
    await message.reply(
        msgs.credits_message.format(credits=credits, amdin=msgs.admin_username),
        reply_markup=return_to_menu,
    )


@bot.on_message(filters.command("buy_credits"))
async def buy_credits_command(client: Client, message: Message):
    if not await user_exists(message.chat.id):
        await message.reply(msgs.user_not_exists)
        return
    chat_id = message.from_user.id

    # Get user's current credits
    user_data = await get_users_columns(chat_id, "credits")
    if user_data is None:
        return

    credits = user_data["credits"]
    btns = create_reply_markup(msgs.go_to_shop_btn)
    await message.reply(
        msgs.buy_credits_message.format(credits=credits),
        reply_markup=btns,
    )


@bot.on_message(filters.command("list"))
async def voice_list_command(client: Client, message: Message):
    if not await user_exists(message.chat.id):
        await message.reply(msgs.user_not_exists)
        return

    btns = create_reply_markup(msgs.voice_list_btn)
    await message.reply(
        msgs.list_msg,
        reply_markup=btns,
    )


@bot.on_message(filters.command("menu"))
async def menu_command(client, message):
    if not await user_exists(message.chat.id):
        await message.reply(msgs.user_not_exists)
        return
    buttons = create_reply_markup(msgs.menu_btns)
    await message.reply(msgs.menu_msg, reply_markup=buttons)


@bot.on_message(filters.command("123"))
async def help123_command(client, message: Message):
    logging.info("123")


@bot.on_message(filters.command("help"))
async def help_command(client, message: Message):
    if not await user_exists(message.chat.id):
        await message.reply(msgs.user_not_exists)
        return
    buttons = create_reply_markup([msgs.return_to_menu_button])
    await message.reply(
        msgs.help_msg.format(admin_username=msgs.admin_username), reply_markup=buttons
    )


@bot.on_message(filters.text)
async def unknown_command(client, message: Message):
    if not await user_exists(message.chat.id):
        await message.reply(msgs.user_not_exists)
        return
    await message.reply(msgs.error_message)


def create_reply_markup(button_list):
    # text,type,data,row
    keyboard = []

    for button in button_list:
        label, button_type, data, row_index = button

        # Create an InlineKeyboardButton based on the button type
        if button_type == "callback":
            btn = InlineKeyboardButton(label, callback_data=data)
        elif button_type == "url":
            btn = InlineKeyboardButton(label, url=data)
        elif button_type == "switch_inline_query":
            btn = InlineKeyboardButton(label, switch_inline_query=data)
        elif button_type == "switch_inline_query_current_chat":
            btn = InlineKeyboardButton(label, switch_inline_query_current_chat=data)
        else:
            raise ValueError(f"Unsupported button type: {button_type}")

        # Add the button to the appropriate row
        while len(keyboard) <= row_index:
            keyboard.append([])

        keyboard[row_index].append(btn)

    return InlineKeyboardMarkup(keyboard)


def create_keyboard(button_list, resize_keyboard=True, one_time_keyboard=False):
    """
    Create a reply keyboard with the given list of button labels.

    Args:
        button_list (list): A list of button labels. Can be a flat list or a nested list for rows.
        resize_keyboard (bool): Whether to resize the keyboard (default is True).
        one_time_keyboard (bool): Whether to hide the keyboard after one use (default is False).

    Returns:
        ReplyKeyboardMarkup: A Pyrogram ReplyKeyboardMarkup object.
    """
    # Check if button_list is a nested list (rows provided explicitly)
    if all(isinstance(item, list) for item in button_list):
        keyboard = [[KeyboardButton(label) for label in row] for row in button_list]
    else:
        # Treat it as a flat list (all buttons in one row)
        keyboard = [[KeyboardButton(label) for label in button_list]]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard,
    )


def file_name_gen(t_id, file_id):
    directory = f"files/{t_id}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    existing_files = os.listdir(directory)
    file_number = len(existing_files) + 1
    return f"{directory}/{file_number}.ogg"


def add_to_files_json(t_id, file_url):
    if os.path.exists("files.json"):
        with open("files.json", "r") as f:
            files = json.load(f)
    else:
        files = {}

    if str(t_id) in files:
        files[str(t_id)].append(file_url)
    else:
        files[str(t_id)] = [file_url]

    with open("files.json", "w") as f:
        json.dump(files, f, indent=4)


def get_files_by_chat_id(chat_id):
    if os.path.exists("files.json"):
        with open("files.json", "r") as f:
            files = json.load(f)
        return files.get(str(chat_id), [])
    return []


def generate_model_list(json_file):
    """
    Generate a list of models grouped by categories, with category names as headers.

    Args:
        json_file (str): Path to the models.json file.

    Returns:
        list: A list of models grouped by categories with headers.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        models = json.load(f)

    # Group models by category
    categories = {}
    for key, model in models.items():
        category = model.get("category", "Uncategorized")
        if category not in categories:
            categories[category] = []
        categories[category].append((key, model))

    model_list = []
    row_number = 0

    # Define category order
    category_order = ["voice_actor", "character", "actor", "celebritie", "singer"]

    # Add models by category with headers in specified order
    for category in category_order:
        if category not in categories:
            continue

        category_models = categories[category]

        # Add category header as a regular button instead of header type
        model_list.append(
            [
                msgs.category_header.format(
                    category=msgs.categories_lable[category], count=len(category_models)
                ),
                "callback",
                f"cat_{category}",
                row_number,
            ]
        )
        row_number += 1

        # Add models in this category
        for i, (key, model) in enumerate(category_models):
            if i % 2 == 0 and i > 0:
                row_number += 1
            model_list.append([model["name"], "callback", f"voice_{key}", row_number])

        row_number += 1  # Add extra row between categories

    return model_list


def get_value_from_json(file_path, key):
    """
    Retrieve the value of a specific key from a JSON file.

    Args:
        file_path (str): Path to the JSON file.
        key (str): The key whose value you want to retrieve.

    Returns:
        any: The value associated with the key, or None if the key doesn't exist.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get(
                key
            )  # Returns the value for the key, or None if it doesn't exist
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
        return None


def joined_channels_button(not_joined_channels):
    buttons = []
    for channel in not_joined_channels:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{channel}", url=f"https://t.me/{channel.replace('@', '')}"
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=msgs.joined_channels_btn[0],
                callback_data=msgs.joined_channels_btn[2],
            )
        ]
    )
    return buttons


async def process_pitch_conversion(
    chat_id: int, data, message, pitch_based_on_gender=None
):
    # check if user has enough credits
    generation = await get_last_generation_by_chat_id(chat_id)
    duration = generation.duration

    user = await get_users_columns(chat_id, "credits")
    credits = user["credits"]

    if credits < duration:
        await message.reply(msgs.no_credits)
        return

    # update user credits
    new_credits = credits - duration
    await update_user_column(chat_id, "credits", new_credits)

    # get pitch | if data has been passed it means it is calling from pitch selection
    if data:
        pitch = int(data.replace("pitch_", ""))

    # it means it has beed detected from gender selection
    elif pitch_based_on_gender is not None:
        pitch = pitch_based_on_gender

    # get model from database
    model_name = generation.model_name

    # get model data from models.json
    model_data = get_value_from_json(MODELS_DIR, model_name)
    model_title = model_data["name"]
    model_url = model_data["url"]
    model_0_pitch = model_data["pitch"]
    audio = generation.input_url
    rvc_model = model_data["type"]

    if not generation.paid:
        # add to generations table
        await update_generations_columns(
            generation.uid,
            {
                "status": Status.inqueue,
                "cost": duration,
                "pitch": pitch + model_0_pitch,
                "model_url": model_url,
            },
        )

        queue_size = await count_queue_items()

        await message.reply(msgs.proccessing_emojie)
        await message.reply(
            msgs.proccessing_queue.format(
                used_credits=duration, credits=new_credits, queue=queue_size
            )
        )

        return

    # create rvc conversion to replicate
    prediction = rvc.create_rvc_conversion(
        model_url,
        chat_id,
        generation.uid,
        generation.id,
        pitch=pitch + model_0_pitch,
        voice_name=model_title,
        rvc_model=rvc_model,
        duration=duration,
        audio=audio,
    )

    # add to generations table
    await update_generations_columns(
        generation.uid,
        {
            "replicate_id": prediction,
            "status": Status.processing,
            "cost": duration,
            "pitch": pitch + model_0_pitch,
            "model_url": model_url,
        },
    )

    await message.reply(msgs.proccessing_emojie)
    await message.reply(
        msgs.proccessing.format(used_credits=duration, credits=new_credits)
    )


# Configure standard logging
logging.basicConfig(level=logging.INFO)

# Configure logfire logging
logfire.info("bot started")
logging.info("bot started")


async def main():
    await init_db()  # Ensure this is awaited
    await bot.start()  # Start the bot
    await idle()  # Keep the bot running


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


logging.info("bot stopped")
# Add logfire shutdown log
logfire.info("bot stopped")
