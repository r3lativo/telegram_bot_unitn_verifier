import mailtrap as mt
from dotenv import load_dotenv
import os, random
from utils import create_html_text, create_sandbox_text
import re
import requests


def validate_email(address):
    unitn_regex = r'^[a-z0-9]+\.?[a-z0-9]+@(studenti\.)?unitn\.it$'

    if re.match(unitn_regex, address):
        return True
    else:
        return False


# Function to create a random 5-digit verification code.
def create_seq():
    seq = ""  
    for i in range(5):  
        seq += str(random.randrange(0, 9))  
    #print("verification code created") 
    return seq


# Function to check if the user input matches the generated verification code.
def check_seq(seq, terminal=True, telegram_code=None):
    if terminal == True:
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
        if telegram_code == seq:
            return True
        else:
            return False


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