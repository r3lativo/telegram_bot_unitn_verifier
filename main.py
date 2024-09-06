from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    PicklePersistence,
    ConversationHandler,
    MessageHandler,
    filters
)
import dotenv, os, logging

from chatbot_funcs import (
    start,
    verify,
    verify_mail,
    code_validation,
    cancel,
    help_command,
    send_invite
)
from chatbot_funcs import (
    TYPING_EMAIL,
    VERIFYING_EMAIL,
    VALIDATING_CODE,
    CANCEL
)


#--------------------------------------------------------------------------------------------------

"""Enable logging"""
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

#--------------------------------------------------------------------------------------------------


def main() -> None:
    """Run the bot."""
    # The token to the chatbot
    dotenv.load_dotenv()
    token = os.getenv("BOT_TOKEN")

    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="pickle_emails")

    application = Application.builder().token(token).persistence(persistence).build()

    # Register the /start command to send the custom keyboard
    application.add_handler(CommandHandler("start", start))

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("verify", verify)],
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
                    cancel
            )
            ],
            CANCEL: [
                MessageHandler(
                    filters.TEXT,
                    cancel
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="mail_conversation",
        persistent=True,
    )
    application.add_handler(CommandHandler("invite", send_invite))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
