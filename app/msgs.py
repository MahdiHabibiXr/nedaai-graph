start = (
    "Hello👋 dear {username}, welcome.\n\n"
    "😎With this bot you can do several things:\n\n"
    "1. You can convert your voice to professional voiceovers, movie and animation characters, and celebrities.\n"
    "2. You can separate the singer's voice from the music of a song (if you want to change the singer of a song, this option will help you)\n\n"
    "✅To start, just send me a voice message or audio file.\n\n"
    "‼️Note that for better voice cloning output, the audio you send should be without noise or extra sounds."
)
gift_msg = "🎁 You have been awarded {inital_credits} seconds of gift credit. \n\n"
joined_channels_btn = ["✅ I Joined", "callback", "joined_channels", 0]
join_channels = (
    "🔻Please join the following channels to start and click the 'I Joined' button\n"
)
voice_select = "🎭 Please select the voice you want to convert to\n\n**To hear voice samples: /list**"
pitch_select = """
🎙 Adjust Voice Pitch

📌If you need the output voice to be deeper or higher, please select one of the options below

🔍 It is recommended to first generate a voice with the **default** option and then adjust the pitch for greater similarity to the selected voice.

"""
pitch_btns = [
    ["🔺 Deeper", "callback", "pitch_-3", 1],
    ["🔺 Much Deeper", "callback", "pitch_-6", 1],
    ["🔸 No Change | Default", "callback", "pitch_0", 2],
    ["🔻 Higher", "callback", "pitch_3", 3],
    ["🔻 Much Higher", "callback", "pitch_6", 3],
]
proccessing_emojie = "⏳"
proccessing = (
    "🔄Processing your request...\n\n"
    "Credits used for this request: **{used_credits} seconds**\n\n"
    "**🔸 Your remaining credits: {credits} seconds**\n\n"
)
proccessing_queue = (
    "🔄 Your request has been added to the processing queue...\n\n"
    "📊 You are #{queue} in the processing queue\n\n"
    "💰 Credits used for this request: **{used_credits} seconds**\n\n"
    "**🔸 Your remaining credits: {credits} seconds**\n\n"
    "✨ Users with premium credits don't wait in queue. Buy credits: /buy_credits"
)
no_credits = """
‼️ You don't have enough credits for this request.

**💰 To increase your credits:**
🔹 Use the /buy_credits command.
🎁 Or use /invite to invite your friends and get gift credits!"""

banner_msg = """
🔥AI Voice Cloning Bot

😍With this bot you can convert your voice to professional voiceovers, movie and animation characters, and even celebrities.

🎙Some of the available voices:
🔻 Raz-e-Bagha Narrator
🔻 Kung Fu Panda
🔻 Shrek 
🔻 Ferdosipour
🔻 Mohsen Chavoshi
and many other exciting voices

✅You can start using it right now through the link below - just send a voice message and it will clone it:"""

invite_help = (
    "🎁 Send the above message to your friends to receive gift credits.\n\n"
    "🔸 Your successful invites: **{refs}**\n\n"
    "🔗 Your invite link:\n{invite_link}\n\n" 
    "🔸 Your remaining credits: **{credits} seconds**\n\n"
    "✅ For each successful invite, you'll receive **{invitation_gift} seconds** of free credit.\n\n"
)

invitation_gift = 40
initial_gift = 60
credits_message = (
    "🔸 Your remaining credits: **{credits} seconds**\n\n📱 Buy subscription: /buy_credits \n\n"
)

categories_lable = {
    "celebritie": "👥 Celebrities",
    "singer": "🎤 Singers", 
    "voice_actor": "🎙️ Voice Actors",
    "character": "🦸 Characters",
    "actor": "🎭 Actors",
}

select_category = "🎭 Please select one of the voices"
category_header = "--==🔻{category} | Number of voices: {count} 🔻==--"
menu_msg = "Welcome, please select an option:"
menu_btns = [
    ["💰 Buy Credits", "callback", "buy_credits", 0],
    ["🎙️ Voice Clone", "callback", "convert_voice", 0], 
    ["🎧 Available Voice Samples", "callback", "list", 1],
    ["🎙 Separate Voice from Music", "callback", "vocal_remover", 2],
    ["📖 Help", "callback", "help", 3],
    ["🎁 Invite Friends", "callback", "invite", 3],
]
help_msg = """
🚦 Neda AI Voice Cloning Bot Guide

🎙 This bot can convert your voice to professional voiceovers, celebrities, movie, TV series and animation characters, and famous singers.

🎤 It can also separate the singer's voice from a song. Then you can use this bot's voice cloning feature to change the singer's voice of that song.

📌 You can use Nedaai to create engaging content, narration and voiceovers for advertising videos and create an engaging video.

🎤 To use this bot, just send a voice message or audio file and select one of the available voice options.

👈Then the bot will ask you about the pitch settings of the final voice, which you need to find the right settings for your voice based on the input voice and selected voice.

- For example, if the voice you sent is relatively deeper than the voice you selected for conversion, you should use the pitch lowering options.

- Then the bot will send you the generated voice with the new voice and you can save it and use it in different places.

❓ If you have any questions, you can ask @nedaaisupport
"""
convert_msg = """
✅To start, just send me a voice message or audio file that is 15 seconds or longer.

‼️Note that for better output, the audio you send should be without noise or extra sounds.

With subscription this limit reduces to 5 seconds. To buy subscription: /buy_credits

"""
vocal_remove_msg = """
✅To start, just send me a song that is 30 seconds or longer.

Then I will separate the singer's voice from the music and send it to you. This way you can send me back the singer's voice and change the singer's voice to someone else.

This feature is temporarily disabled
"""
admin_id = 791927771  
admin_username = "@nedaaisupport"
return_to_menu_button = ["Return to Main Menu", "callback", "menu", 0]
error_message = (
    "❌ Invalid command, click /menu to enter main menu\n\n"
    "🎤 To clone voice, please send a voice message or audio file"
)
t40_price = 0.000225  # per second
invite_successfully = (
    "✨ User {user} joined the bot with your invite link.\n\n"
    "🎁 {gift_credits} seconds of credit was awarded to you.\n\n"
)
channels_list = ["@nedaaiofficial"]
banner_img_id = "AgACAgQAAxkBAAIBSmgohGpmJBBuP_IEg-rjfgpomsKzAAIfxzEbBmlAUZ0HBaw4EyBTAAgBAAMCAAN5AAceBA"
gender_select = """
👥 Please select the gender of your input voice:
"""
gender_btns = [
    ["👩 Female", "callback", "gender_female", 0], 
    ["👨 Male", "callback", "gender_male", 0],
]
added_credits = (
    "✨ Dear user, {credits} seconds of credit have been added to your account.\n\n"
    "🔸 Your remaining credits: {new_credits}"
)
task_msg = """
🎤 What would you like me to do?

👈To convert your voice to different voices, select the 'Voice Clone' option

👈To separate a singer's voice from the music and instruments of a song, use the 'Separate Voice from Music' option. This feature is temporarily disabled
"""
task_btns = [
    ["🔊 Voice Clone", "callback", "task_voice_changer", 0],
    # ["🎙 Separate Voice from Music (Disabled)", "callback", "none", 1],
]
bot_id = 7760580398
short_audio = """⛔️ Your input voice must not be less than {limit} seconds

To remove this limitation, you can purchase premium credits. Order: /buy_credits"""
short_audio_paid = "⛔️ Your input voice must not be less than {limit} seconds"
short_audio_for_vocal_remove = "⛔️ Your input song must not be less than {limit} seconds"
convert_limit = 15
convert_limit_paid = 5
vocal_remove_limit = 60
vocal_remove_limit_paid = 30
uploading_file = "🔄 Uploading file..."
unknown_error = "An unknown error occurred, please try again!"
user_not_exists = "‼️ You haven't joined our bot yet, click /start to begin."
already_inqueue = """‼️ You have a request being processed. You cannot submit a new request until the previous one is completed. ⏳

To remove the limitation on simultaneous requests, you can purchase premium credits through the /buy_credits command. 💳"""

buy_credits_message = (
    # "💰 Buy Credits\n\n"
    "🔸 Your remaining credits: **{credits} seconds**\n\n"
    "**📩 To learn about prices and purchase voice cloning bot subscription, join this channel: @nedaaisub\n\n**"
    "✨ With subscription, use the bot without waiting in processing queue!"
)

prices = {
    "15": 99000,  # 100
    "30": 190000,  # 200
    "60": 375000,  # 400
    "120": 745000,  # 800
    "180": 1100000,  # 1200
}

buy_credits_btn = [
    [
        "💳 15 Minutes Package",
        "url",
        "https://t.me/nedaaisupport?text=Hi, I want to buy the 15 minutes voice cloning bot package",
        0,
    ],
    [
        "💳 30 Minutes Package",
        "url",
        "https://t.me/nedaaisupport?text=Hi, I want to buy the 30 minutes voice cloning bot package",
        1,
    ],
    [
        "💳 60 Minutes Package", 
        "url",
        "https://t.me/nedaaisupport?text=Hi, I want to buy the 60 minutes voice cloning bot package",
        2,
    ],
    [
        "💳 120 Minutes Package",
        "url",
        "https://t.me/nedaaisupport?text=Hi, I want to buy the 120 minutes voice cloning bot package",
        3,
    ],
    [
        "💳 180 Minutes Package",
        "url",
        "https://t.me/nedaaisupport?text=Hi, I want to buy the 180 minutes voice cloning bot package",
        4,
    ],
    ["⬅️Return to Main Menu", "callback", "menu", 5],
]

go_to_support_btn = [
    [
        "💳 Buy Premium Credits",
        "url",
        "t.me/nedaaisupport",
        0,
    ],
    ["⬅️Return to Main Menu", "callback", "menu", 5],
]
go_to_shop_btn = [
    [
        "💳 Buy Premium Credits",
        "url",
        "https://t.me/nedaaisub",
        0,
    ],
    ["⬅️Return to Main Menu", "callback", "menu", 1],
]
voice_list_btn = [
    ["🎧 Neda AI Voice Samples", "url", "https://t.me/nedaaiofficial/46", 0],
    ["⬅️Return to Main Menu", "callback", "menu", 1],
]

list_msg = """
**🎙Click the button below to hear voice samples of available Neda bot models.**"""
