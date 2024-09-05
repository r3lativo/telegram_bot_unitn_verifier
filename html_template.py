
def create_message(seq):
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
