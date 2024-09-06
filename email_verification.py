import mailtrap as mt
from dotenv import load_dotenv
from random import randrange
from utils import (
    create_html_text,
    create_sandbox_text
)
import re, os, requests

#--------------------------------------------------------------------------------------------------

MAIL_REGEX = r'[a-z0-9]+[\.\_]?[a-z0-9]+?@(\w+\.)?\w+\.\w+'
UNITN_REGEX = r'[a-z0-9]+[\.\_]?[a-z0-9]+?@(\w+\.)?unitn\.it'
SEQ_LENGHT = 5

#--------------------------------------------------------------------------------------------------

def validate_email(address):
    """Checks whether it resembles an email"""
    return True if re.match(MAIL_REGEX, address) else False


def validate_unitn_domain(address):
    """Checks whether the email domain is unitn"""
    UNITN_REGEX = r'[a-z0-9]+[\.\_]?[a-z0-9]+?@(\w+\.)?unitn\.it'
    return True if re.match(UNITN_REGEX, address) else False


# Function to create a random 5-digit verification code.
def create_seq():
    # A random sequence
    seq = ''.join(str(randrange(0, 9)) for _ in range(SEQ_LENGHT))
    #print("verification code created") 
    return seq


# Function to check if the user input matches the generated verification code.
def check_seq(seq, telegram_code=None):
    if telegram_code == None:
        while True:
            user_input = input("enter your code here: ")  
            if len(user_input) != len(seq):
                print(f"you need a {len(seq)}-digit code")  
            else: break  # Exit the loop if the code length is correct.

        if user_input == seq:
            print("You're in!")
            return True
        else:
            print("OUT!")
            return False
    
    # Telegram
    else:
        return True if telegram_code == seq else False


def send_seq(email_address="r3lativo@outlook.it", debug=True, sandbox=True):

    seq = create_seq()
    load_dotenv()  # The api token to send the email via mailtrap
    
    if sandbox == True:
        url = "https://sandbox.api.mailtrap.io/api/send/3122557"
        sandbox_token = os.getenv("MAILTRAP_SANDBOX_BEARER")

        payload = create_sandbox_text(seq)
        headers = {
        "Authorization": f"Bearer {sandbox_token}",
        "Content-Type": "application/json"
        }
        response = requests.request("POST", url, headers=headers, data=payload)

    else:
        # Create the email message with the subject, sender, receiver, and verification code.
        api_token = os.getenv("MAILTRAP_API")

        mail = mt.Mail(
            sender=mt.Address(email="mailtrap@demomailtrap.com", name="Mailtrap Test"),
            to=[mt.Address(email=email_address)],
            subject="Verify your email",
            html=create_html_text(seq),
        )
        # Load the client
        client = mt.MailtrapClient(token=api_token)
        # Send the email
        response = client.send(mail)

    if debug == True:
        # Print the response of the client (for debugging purposes).
        print(f"response: {response}")
        # Print the verification code (for debugging purposes).
        print(f"SEQUENCE: {seq}")

    # Prompt the user to enter the verification code and check it.
    return seq


def example():
    # Create the verification code, send it and store it
    seq = send_seq()
    
    # Check that it is valid
    check_seq(seq=seq, terminal=True)

#example()