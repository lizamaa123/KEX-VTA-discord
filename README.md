# Virtual Teaching Assistant for C programming students 

This is a Discord bot powered by Azure OpenAI's GPT model. The bot acts as a virtual teaching assistant (VTA) to help students improve their problem-solving skills in C programming, with tailored guidance for users who may have prior experience in Python programming. This project has been co-developed with Microsoft Copilot and ChatGPT-4.

## About the Authors

This bot was created by **Liza Aziz** and **Olivia Strömbom** as part of our bachelor thesis at the **KTH  Royal Institute of Technology (Media Technology Chapter)**.

## Features

- Provides guided feedback to students' questions and problems.
- Adapts responses based on the user's language and programming experience.
- Handles conversation history to maintain context.
- Resets conversation history for new questions or problems.
- Integrates with Azure OpenAI for generating responses.

## Prerequisites

Before running the bot, ensure you have the following:

1. Python 3.8 or higher installed.
2. A `.env` file with the following environment variables:
   - `DISCORD_TOKEN`: Your Discord bot token.
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key.
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint.
   - `AZURE_OPENAI_DEPLOYMENT`: Your Azure OpenAI deployment name.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/KEX-VTA-discord.git
   cd KEX-VTA-discord

**Important:**  
This bot is a work in progress and can still be developed further. There are many opportunities to enhance its functionality, improve its responses and add new features.