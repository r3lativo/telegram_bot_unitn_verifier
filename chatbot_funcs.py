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
from datetime import datetime, timedelta

from email_verification import send_seq, check_seq, validate_email
from utils import new_attempt_time_check

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
max_attempts = 3


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_text = f"Hello, {user.username}!\n"

    # If there is already a chat log with the user
    if context.user_data:
        if context.user_data["validated"] == True:  # commented until i don't create the "verification"
            reply_text += (
                "We already verified your email, bye!"
            )
            # Reply and end conversation
            await update.message.reply_text(reply_text)
            return ConversationHandler.END
        
        if context.user_data["time_of_fail"] != None:
            new_attempt_state, retry_time = new_attempt_time_check(context.user_data["time_of_fail"])
            # If the check fails
            if new_attempt_state == False:
                await update.message.reply_text(
                    f"Less than 24 hours have passed. Please retry on {retry_time}"
                )
                return ConversationHandler.END

        else:
            reply_text += (
                "Let' try to validate your email again. What is your institutional email?"
            )
            await update.message.reply_text(reply_text)
            return TYPING_EMAIL

    # If there is no data on the user
    else:
        # Create the number of attempts left
        context.user_data["attempts_left"] = max_attempts
        context.user_data["time_of_fail"] = None
        reply_text += (
            "To access the rest of the group topics, let's verify your email.\n"
            "Please enter your institutional email (ending with 'unitn it')"
            )
        # Ask for email
        await update.message.reply_text(reply_text)
        # Go into the typing email case
        return TYPING_EMAIL


async def verify_mail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stores the email if valid, and sends the verification code"""
    text = update.message.text
    EMAIL_ADDRESS = text
    # Store the email address
    context.user_data["email_address"] = text.lower()

    # VALIDATING ALGORITHM HERE
    if validate_email(EMAIL_ADDRESS) == True:
        await update.message.reply_text(
            f"{text} is a valid unitn email"
        )
        time.sleep(1)

        # VERIFYING ALGORITHM HERE
        global SEQUENCE
        SEQUENCE = send_seq(debug=True, sandbox=True)#, email_address=EMAIL_ADDRESS)

        await update.message.reply_text(
            f"A verification code has been sent to {EMAIL_ADDRESS}! Please insert it here to complete verification."
        )
        return VERIFYING_EMAIL
    else:
        await update.message.reply_text(
            f"{text} is not a valid unitn email."
        )
        time.sleep(1)
        await update.message.reply_text(
            f"Please insert an email in the format yourname@[studenti.]unitn.it"
        )
        return TYPING_EMAIL


async def code_validation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    # If the user already failed once
    if context.user_data["time_of_fail"] != None:
        stored_time = context.user_data["time_of_fail"]
        new_attempt_state, retry_time = new_attempt_time_check(stored_time)
        # If the check fails
        if new_attempt_state == False:
            await update.message.reply_text(
                f"Less than 24 hours have passed. Please retry on {retry_time}"
            )
            return ConversationHandler.END

    input_code = update.message.text
    print(f"code: {input_code}")

    if len(input_code) != 5:
        await update.message.reply_text(
            f"you need a {len(SEQUENCE)}-digit code"
        )
        return VERIFYING_EMAIL

    state_check = check_seq(seq=SEQUENCE, terminal=False, telegram_code=input_code)
    
    if state_check == True:
        await update.message.reply_text(
            "The code is correct!"
        )
        context.user_data["validated"] = True

        # TODO SEND TO INVITE LINK TO GROUP CREATION
        return DONE
    
    elif state_check == False and context.user_data["attempts_left"] > 0:
        context.user_data["validated"] = False
        context.user_data["attempts_left"] -= 1
        await update.message.reply_text(
            f"The code {input_code} is not correct.\nYou have {context.user_data["attempts_left"]} attempts left"
        )
        return VERIFYING_EMAIL
    
    else:
        await update.message.reply_text(
            f"The code {input_code} is not correct.\n No more attempts left. Please try again in 24 hours."
        )
        context.user_data["time_of_fail"] = datetime.now()
        context.user_data["validated"] = False
        return ConversationHandler.END
     


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