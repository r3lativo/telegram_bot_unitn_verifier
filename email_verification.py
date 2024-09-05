import mailtrap as mt
from dotenv import load_dotenv
import os, random
from html_template import create_message



# Function to create a random 5-digit verification code.
def create_seq():
    seq = ""  
    for i in range(5):  
        seq += str(random.randrange(0, 9))  
    #print("verification code created") 
    return seq


# Function to check if the user input matches the generated verification code.
def check_seq(seq, terminal, telegram_code=None):
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


#--------------------------------------------------



def send_seq(email_address="r3lativo@outlook.it", terminal=True):

    seq = create_seq()

    # The api token to send the email via mailtrap
    load_dotenv()
    api_token = os.getenv("MAILTRAP_API")


    # Create the email message with the subject, sender, receiver, and verification code.
    mail = mt.Mail(
        sender=mt.Address(email="mailtrap@demomailtrap.com", name="Mailtrap Test"),
        to=[mt.Address(email=email_address)],
        subject="Verify your email",
        html=create_message(seq),
    )

    # Load the client
    client = mt.MailtrapClient(token=api_token)

    if terminal == False:
        # Send the email
        response = client.send(mail)
        # Print the response of the client (for debugging purposes).
        print(response)

    # Print the verification code (for debugging purposes).
    #print(seq)

    # Prompt the user to enter the verification code and check it.
    return seq

# Create the verification code


def main():
    seq = send_seq()
    check_seq(seq=seq)
