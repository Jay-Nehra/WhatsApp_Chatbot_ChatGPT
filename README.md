# WhatsApp Chatbot Using Flask, Twilio, and OpenAI API

## Description

This project implements a WhatsApp chatbot using the Flask web framework, Twilio for WhatsApp messaging, and OpenAI's GPT-3 API for generating conversational responses. The chatbot is designed to provide tailored travel itineraries based on user input.

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Database](#database)
5. [Environment Variables](#environment-variables)
6. [Testing](#testing)
7. [Contributing](#contributing)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)

## Requirements

- Python 3.x
- Flask
- Twilio SDK
- OpenAI Python SDK
- TinyDB

## Installation

1. Clone the repository:

   ```bash
   git clone https://https://github.com/Jay-Nehra/WhatsApp_Chatbot_ChatGPT.git
   ```
Navigate to the project directory:

```bash
cd path/to/project
```
Install required packages:

```bash
pip install -r requirements.txt
```
## Usage
1. Set up your environment variables for Twilio and OpenAI API keys.

2. un the Flask app:

```bash
flask run
```
3. Use your WhatsApp to interact with the bot by sending a message to the Twilio phone number.

## Database
We use TinyDB as an in-memory database to store conversations. The database is stored in the tmp directory.

## Environment Variables
1. OPENAI_API_KEY: Your OpenAI API Key
2. TWILIO_ACCOUNT_SID: Your Twilio Account SID
3. TWILIO_AUTH_TOKEN: Your Twilio Auth Token

## Testing
To run tests, execute:

```bash
pytest
```
## Contributing
Feel free to contribute to this project. Create issues, feature requests or pull requests.

## License
MIT License. See LICENSE for more information.

## Acknowledgments
OpenAI for their conversational model
Twilio for their messaging API
Flask for the web framework
