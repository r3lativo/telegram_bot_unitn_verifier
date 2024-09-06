from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from datetime import datetime, timedelta
import time, re, os
from random import randrange
from email_verification import (
    send_seq,
    check_seq,
    SEQ_LENGHT
)
from utils import new_attempt_time_check
import dotenv

#--------------------------------------------------------------------------------------------------

"""Define some constants and variables"""
TYPING_EMAIL, VERIFYING_EMAIL, VALIDATING_CODE, CANCEL, INVITE = range(5)

basic_mail_regex = r'[a-z0-9]+[\.\_]?[a-z0-9]+?@(\w+\.)?\w+\.\w+'
unitn_regex = r'[a-z0-9]+[\.\_]?[a-z0-9]+?@(\w+\.)?unitn\.it'

code_regex = r"\b\d{5}\b"
max_attempts = 3

dotenv.load_dotenv()
cimec_chat_id = os.getenv("CIMeC_CHAT_ID")

#--------------------------------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Define the custom keyboard layout
    keyboard = [
        ["/verify", "/invite"],  # First row of buttons
        ["/help", "/cancel"]  # Second row of buttons
    ]
    
    # Create a ReplyKeyboardMarkup object
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Send a message with the custom keyboard
    await update.message.reply_text(
        "Choose a command:",
        reply_markup=reply_markup
    )


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /verify is issued."""
    user = update.effective_user
    ask_for_inst_email = f"Please type your institutional email address (the one ending with `unitn.it`)."
    reply_text = f"Hello, {user.username}! "

    # If there is already a chat log with the user
    if context.user_data:
        
        # If the user is already verified, end conversation
        if context.user_data["verified"] == True:
            reply_text += (
                f"We already verified your email, bye!"
                # TODO ADD /help AND LET SEE THE STORED INFO
            )
            # Reply and end conversation
            await update.message.reply_text(reply_text)
            return ConversationHandler.END
        
        # If the user failed the verification, check whether they can retry
        if context.user_data["time_of_fail"] != None:
            new_attempt_state, retry_time = new_attempt_time_check(context.user_data["time_of_fail"])
            # If the check fails
            if new_attempt_state == False:
                await update.message.reply_text(
                    f"Less than 24 hours have passed. Please retry on {retry_time}"
                )
                return ConversationHandler.END
        
        # If the user did not verify email yet
        else:
            context.user_data["attempts_left"] = max_attempts
            reply_text += f"Let' try to validate your email again."
            await update.message.reply_text(reply_text)
            time.sleep(2)
            await update.message.reply_text(ask_for_inst_email)
            return TYPING_EMAIL

    # If there is no data on the user
    else:
        # Create basic variables on user
        context.user_data["attempts_left"] = max_attempts
        context.user_data["time_of_fail"] = None
        context.user_data["invite_created"] = None

        reply_text += (
            f"To get access to the CIMeC groupchat, we need to verify you are part of UniTn. "
            f"I'll send you a verification code on your email."
            )
        # Ask and wait for email
        await update.message.reply_text(reply_text)
        time.sleep(1)
        await update.message.reply_text(ask_for_inst_email)
        # Go into the typing email case
        return TYPING_EMAIL


async def verify_mail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stores the email if valid, and sends the verification code"""
    email_format = f"Please type an email in the format of `yourname@[studenti.]unitn.it`."
    
    # Check that the text contains a valid email
    text = update.message.text
    reply = ""

    # Store the email if it's there
    basic_match = re.search(basic_mail_regex, text)
    if basic_match:
        input_address = basic_match.group()
        reply += f"`{input_address}` seems to be a valid email address"
    else:
        reply += f"`{text}` doesn't seems like a valid email address..."
        await update.message.reply_text(reply)
        time.sleep(1)
        await update.message.reply_text(email_format)
        return TYPING_EMAIL

    # Check whether the domain is unitn
    unitn_match = re.search(unitn_regex, text)
    if unitn_match:
        final_address = unitn_match.group()
        final_address = final_address.lower()
        context.user_data["email_address"] = final_address
        # Create verification code
        global SEQUENCE
        SEQUENCE = send_seq()#debug=True, sandbox=False, email_address=input_address)
        reply += f", and also part of the `unitn.it` domain."
        await update.message.reply_text(reply)
        time.sleep(1)
        await update.message.reply_text(
            f"A verification code has been sent to `{final_address}`! Please insert it here to complete verification."
            )
        time.sleep(1)
        await update.message.reply_text(
            f"Remember to also check your spam!"
            )
        return VERIFYING_EMAIL
    else:
        reply += f", but not part of the `unitn.it` domain."
        reply += email_format
        await update.message.reply_text(reply)
        return TYPING_EMAIL


async def code_validation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check whether the conde inputed and the one created are the same"""
    # If the user already failed once
    if context.user_data["time_of_fail"] != None:
        # Check whether they can try again
        stored_time = context.user_data["time_of_fail"]
        new_attempt_state, retry_time = new_attempt_time_check(stored_time)
        # If the check fails, end conversation
        if new_attempt_state == False:
            await update.message.reply_text(
                f"Less than 24 hours have passed. Please retry on {retry_time}"
            )
            return ConversationHandler.END

    text = update.message.text

    # Check that the text contains a right kind of sequence
    match = re.search(code_regex, text)
    if match:
        input_sequence = match.group()
        print(f"input sequence: {input_sequence}")  # Debug
    else:
        eg = ''.join(str(randrange(0, 9)) for _ in range(SEQ_LENGHT))
        await update.message.reply_text(
            f"You need a {SEQ_LENGHT}-digit code, like `{eg}`"
        )
        return VERIFYING_EMAIL
    
    # Run the check
    state_check = check_seq(seq=SEQUENCE, telegram_code=input_sequence)
    
    # If the code is of the right kind but incorrect, and still have attempts left
    if state_check == False:
        context.user_data["verified"] = False
        context.user_data["attempts_left"] -= 1

        if context.user_data["attempts_left"] > 0:
            await update.message.reply_text(
                f"The code {input_sequence} is not correct. You have {context.user_data["attempts_left"]} attempts left."
            )
            return VERIFYING_EMAIL
        # If no attempts left
        else:
            await update.message.reply_text(
                f"The code {input_sequence} is not correct."
            )
            time.sleep(1)
            await update.message.reply_text(
                f"No more attempts left. Please try again in 24 hours."
            )
            context.user_data["time_of_fail"] = datetime.now()
            context.user_data["verified"] = False
            return ConversationHandler.END
    
    # If there is a match
    else:
        await update.message.reply_text(
            "Verification process completed! Now please type /invite to get the invite link to the CIMeC group chat!"
        )
        context.user_data["verified"] = True
        return ConversationHandler.END
    

async def send_invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    """Send invite link to group chat"""
    # No data on the user
    if not context.user_data or context.user_data["verified"] == False:
        await update.message.reply_text(
            f"To get the invite link, first verify your email with /verify.\n"
            f"Type /help to know more."
        )
        return ConversationHandler.END
    
    # Invite already created
    if context.user_data["invite_created"] != None:
        await update.message.reply_text(
            f"Your invite link was already created on {context.user_data["invite_created"]}. "
            f"If something went wrong, type /help or contact @djuone for assistance."
        )
        return ConversationHandler.END

    # Have data on the user but no invite was created
    else:
        # Create link to CIMeC group chat
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=cimec_chat_id,
            expire_date=datetime.now() + timedelta(hours=24),  # Set expiration to 24 hours
            member_limit=1,  # Limit the number of users who can join via this link
            )

        # Send the invite link to the user
        await update.message.reply_text(
            f"Here is your invite link: {invite_link.invite_link}\n"
            f"Expires on: {invite_link.expire_date}\n"
            f"Member limit: {invite_link.member_limit}"
        )
        context.user_data["invite_created"] = datetime.now()
        return ConversationHandler.END
    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Hello! I'm here to help you get access to our group chat.\n\n"
        "To verify your email address, please use the /verify command. "
        "Once your email is verified, you'll receive an invite to join the group.\n\n"
        "Please note that you only get one invite per person. If you encounter any issues, "
        "feel free to contact @djuone for assistance."
    )
    await update.message.reply_text(help_text)
    

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        f"I learned these facts about you:\n"
        f"{context.user_data}\n"
        f"Until next time!"
    )
    file_path = "pickle_emails"

    if os.path.exists(file_path):
        # File exists, proceed with deletion
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File does not exist.")
    return ConversationHandler.END
