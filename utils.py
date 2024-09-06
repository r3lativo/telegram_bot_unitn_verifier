from datetime import datetime, timedelta

def new_attempt_time_check(datetime_stored):
    date_time_now = datetime.now()
    time_difference = abs(date_time_now - datetime_stored)
    #print(f"stored:     {datetime_stored}\ncurrent:    {date_time_now}\ndifference: {time_difference}")
    new_attempt_state = False

    # Check if the difference is 24 hours or more
    if time_difference >= timedelta(hours=24):
        retry_time=None
        #print("The two datetime values are MORE than 24 hours apart.")
        new_attempt_state = True
    else:
        retry_time = datetime_stored + timedelta(hours=24)
        #print("The two datetime values are LESS than 24 hours apart.")
        #print(f"Try again on {retry_time}")
        new_attempt_state = False
    return new_attempt_state, retry_time

def create_sandbox_text(seq):
    text_from = "\"from\":{\"email\":\"mailtrap@example.com\",\"name\":\"Mailtrap Test\"}"
    text_to =   "\"to\":[{\"email\":\"r3lativo@outlook.it\"}]"
    subject =   "\"subject\":\"Please Verify Your Email Address\""
    text_1 =      "\"text\":\"Thank you for signing up! "
    text_2 =      f"To complete your registration, please verify your email address by entering the following verification code: {seq}\""
    text_final = text_1 + text_2
    category =  "\"category\":\"Integration Test\""

    payload = f"{{{text_from},{text_to},{subject},{text_final},{category}}}"

    return payload


def create_html_text(seq):
    message = f"""\
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .header {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .code {{
                font-size: 20px;
                font-weight: bold;
                color: #333;
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
                margin-bottom: 20px;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 14px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Please Verify Your Email Address</div>

            <p>Dear User,</p>

            <p>Thank you for signing up!</p>

            <p>To complete your registration, please verify your email address by entering the following verification code:</p>

            <div class="code">{seq}</div>

            <p>If you did not request this, please ignore this email.</p>
        </div>
    </body>
    </html>
    """
    return message

    
    
def example():
    datetime_stored = datetime(year=2024, month=9, day=6, hour=10, minute=0, second=0)
    new_attempt_time_check(datetime_stored)

#example()