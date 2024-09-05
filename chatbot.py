from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)

from dotenv import load_dotenv
import os
import logging
import time

from email_verification import send_seq, check_seq

# The token to the chatbot
load_dotenv()
token = os.getenv("BOT_TOKEN")



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
















































TYPING_EMAIL, VERIFYING_EMAIL, VALIDATING_CODE, DONE = range(4)

EMAIL_ADDRESS = ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_text = f"Hello, {user.username}!\n"

    # If there is already a chat with the user
    if context.user_data:
        if context.user_data["validated"] == True:  # commented until i don't create the "verification"
            reply_text += (
                "We already verified your email, bye!"
            )
            # Reply and end conversation
            await update.message.reply_text(reply_text)
            return ConversationHandler.END
        else:
            reply_text += (
                "What's up?"
            )
            await update.message.reply_text(reply_text)
            return TYPING_EMAIL

    # If there is no data on the user
    else:
        reply_text += (
            "To access the rest of the group topics, let's verify your email.\n"
            "Please enter your institutional email (ending with 'unitn it')"
            )
        # Ask for email
        await update.message.reply_text(reply_text)
        # Go into the typing email case
        return TYPING_EMAIL


async def verify_mail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    EMAIL_ADDRESS = text
    # Store the email address
    context.user_data["email_address"] = text.lower()

    # TODO VALIDATING ALGORITHM HERE
    # TODO VERIFYING ALGORITHM HERE
    # TODO CASES WHETHER IT IS VALID OR NOT

    await update.message.reply_text(
        f"{text} seems like a good email!"
    )
    time.sleep(1)

    global SEQUENCE
    SEQUENCE = send_seq()#email_address=EMAIL_ADDRESS, terminal=False)
    print(f"SEQUENCE: {SEQUENCE}")

    await update.message.reply_text(
        f"A verification code has been sent to {EMAIL_ADDRESS}! Please insert it here to complete verification."
    )
    return VERIFYING_EMAIL


async def code_validation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    print(f"code: {text}")

    if len(text) != 5:
        await update.message.reply_text(
            f"you need a {len(SEQUENCE)}-digit code"
        )
        return VERIFYING_EMAIL

    state = check_seq(seq=SEQUENCE, terminal=False, telegram_code=text)
    
    if state == True:
        await update.message.reply_text(
            "The code is correct!"
        )
        context.user_data["validated"] = True

        # TODO CREATE INVITE LINK TO GROUP
        return DONE
    else:
        await update.message.reply_text(
            "The code is wrong, retry later"
        )
        context.user_data["validated"] = False
        return ConversationHandler.END
    return
     


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        f"""I learned these facts about you:
        {context.user_data}
        Until next time!""",
    )
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="mailing")
    application = Application.builder().token(token).persistence(persistence).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TYPING_EMAIL: [
                MessageHandler(
                    filters.TEXT,
                    verify_mail
                )
            ],
            VERIFYING_EMAIL: [
                MessageHandler(
                    filters.TEXT,
                    code_validation
                )
            ],
            VALIDATING_CODE: [
                MessageHandler(
                    filters.TEXT,
                    done
            )
            ],
            DONE: [
                MessageHandler(
                    filters.TEXT,
                    done
                )
            ]
        },
        fallbacks=[CommandHandler("done", done)],
        name="mail_conv",
        persistent=True,
    )

    application.add_handler(conv_handler)


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()