## Chatbot for UniTn Email Verification

This repository contains the Python code for a Telegram bot that verifies users' email addresses before granting them access to the CIMeC group chat.

Unfortunatley it does not work, as it needs a payed domain to actually send the email.

**Features:**

* **Email Verification:** Users can verify their email addresses using a verification code sent to their inbox. Only email addresses ending in `unitn.it` are accepted.
* **Conversation Management:** The bot utilizes a conversation flow to guide users through the verification process.
* **Multiple Attempts:** Users have a limited number of attempts to enter the correct verification code.
* **Invite Link Generation:** Upon successful verification, users can receive a personalized invite link to join the CIMeC group chat.

**Requirements:**

* Python 3.x
* Telegram Bot API token (not included)
* Mailtrap account (for email sending)

**Setup:**

1. Clone this repository.
2. Install required dependencies using `pip install -r requirements.txt`.
3. Create a `.env` file in the project root directory and add the following environment variables:
    * `BOT_TOKEN`: Your Telegram bot token
    * `MAILTRAP_API`: Your Mailtrap API token
    * `MAILTRAP_SANDBOX_BEARER`: Your Mailtrap Sandbox API token (optional)
    * `CIMeC_CHAT_ID`: The Telegram chat ID of the CIMeC group chat
4. Update the `email_verification.py` file with your desired email sending options (production or sandbox).

**Usage:**

1. Deploy the bot to a suitable hosting platform (e.g., Heroku).
2. Obtain the Telegram bot token and add the bot to your desired Telegram group chat.

**Code Structure:**

* `main.py`: The main script responsible for initializing the bot and handling user interactions.
* `chatbot_funcs.py`: Contains the core functionality of the bot, including conversation management, user data handling, and verification logic.
* `utils.py`: Provides utility functions used by other parts of the code, such as checking for retry eligibility and creating email content.

**Further Development:**

* Implement error handling and logging mechanisms.
* Enhance user experience with additional commands or features.
* Integrate with a user database for persistent data storage.


**Explanation of utils.py functions:**

* `new_attempt_time_check`: This function checks if a certain amount of time (24 hours) has passed since a previous attempt was made. It returns a boolean indicating whether a new attempt is allowed and optionally the time for the next attempt.
* `create_sandbox_text`: This function constructs the payload for sending an email using Mailtrap's sandbox environment. It defines the sender, recipient, subject, and message body.
* `create_html_text`: This function generates HTML content for an email containing a verification code. It includes styling for a user-friendly presentation.
