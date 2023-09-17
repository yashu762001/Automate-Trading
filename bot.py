from twilio.rest import Client

# Your Twilio Account SID and Auth Token
account_sid = 'AC00db279d7080629f86c96162e2d5a9db'
auth_token = 'f2ca0e254cf68f64259f8c0d62f2daa2'

# Initialize the Twilio client
client = Client(account_sid, auth_token)

# Define your list of keyword-response pairs
keywords = {
    'price1': 'The price of product 1 is $100.',
    'price2': 'The price of product 2 is $200.',
    'price3': 'The price of product 3 is $300.',
    # Add more keywords and responses as needed
}

# Receive messages

while(True):
    messages = client.messages.list(
        from_='whatsapp:+919783049361')  # Your number

    for msg in messages:
        # Process the incoming message text
        # Convert to lowercase for case-insensitive matching
        received_text = msg.body.lower()

        # Search for keywords and send corresponding response
        response_sent = False
        for keyword, response in keywords.items():
            if keyword in received_text:
                client.messages.create(
                    body=response,
                    from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
                    to=msg.from_
                )
                response_sent = True
                break  # Stop searching for keywords once a match is found

        # If no keyword match was found, send a default response
        if not response_sent:
            client.messages.create(
                body="Sorry, I couldn't understand your request.",
                from_='whatsapp:+14155238886',  # Your Twilio WhatsApp number
                to=msg.from_
            )
