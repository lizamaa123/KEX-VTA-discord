# IMPORTING LIBRARIES
import os
from dotenv import load_dotenv
import openai
import discord
from discord.ext import commands
import asyncio

# Downloading environmental variables (.env file)
load_dotenv()

# Discord intents (what the chatbot has access to) 
intents = discord.Intents.default()
intents.message_content = True

# API-keys and endpoints
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT") 
OPENAI_API_VERSION = "2024-07-01-preview"

# Configure Azure OpenAI APIs
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_version = OPENAI_API_VERSION

# Discord bot class
class ChatGPTBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.user_histories = {}  # Saving the conversation history from the user

    def _get_default_user_history(self):
        # Returns the default user history structure.
        return [
            {
                "role": "system",
                "content": (
                    "You are a teaching assistant that helps students develop their problem-solving skills in C programming. The students may have prior experience in Python programming."
                    "You should adapt your responses based on the student's language. \n\n"

                    "## Interaction Rules:\n"
                    "- When a user asks a question or presents a problem give guided feedback and avoid providing immediate answers and solutions. \n"
                    "- Never give the solutions or answers in a full code block, it should always be given as increments so users cannot copy and paste directly.\n"
                    "- If the user provides a code block make sure to answer by guiding first and then asking the student if they want the completed output.\n"
                    "- If the user provides terminal error messages or tracebacks, you should **always** give explanations so the student understand. \n"

                    "If the user is still uncertain of that specific problem or question after the third time, that is when you can provide with immediate answers and solutions\n"

                    "- This should be applied to all user queries, regardless of the topic or nature of the question.\n"
                    "- If a user initiates a new question/problem, make sure to follow the structure above **from the beginning**.\n"
                    "- If a user submits a code snippet or a partial attempt and requests help, follow the same process.\n\n"

                    "## Important Considerations:\n"
                    "- Always respond in the user's language.\n"
                    "- Never give the solutions or answers in a full code block, it should always be given as increments so users cannot copy and paste directly.\n"
                    "- When a user asks a question or presents a problem give guided feedback and avoid providing immediate answers and solutions. \n"
                    "- If a user writes in a language you do not recognize, ask them to specify their preferred language for the response.\n"
                    "- If a response exceeds 2000 tokens, inform the user and split the response into smaller parts."
                )
            }
        ]

    async def on_ready(self):
        print(f"✅ {self.user} is now online and ready to chat with!")
        print(f"Environment Variables:")
        print(f"DISCORD_TOKEN: {os.getenv('DISCORD_TOKEN')}")
        print(f"AZURE_OPENAI_API_KEY: {os.getenv('AZURE_OPENAI_API_KEY')}")
        print(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"AZURE_OPENAI_DEPLOYMENT: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
        print(f"OPENAI_API_VERSION: {os.getenv('OPENAI_API_VERSION')}")

    async def on_message(self, message):
        if message.author == self.user:
            return  # Ignoring the bot's own messages

        user_id = message.author.id  # Unique ID per user 
        query = message.content

        # Send a "thinking" message while generating a response (for user feedback)
        thinking_message = await message.channel.send("⏳ **VTA genererar ett svar...**")

        # If the user is new, a new chat history will be made 
        if user_id not in self.user_histories:
            self.user_histories[user_id] = self._get_default_user_history()

        # Check if the user is asking a new question
        is_new_question = self._is_new_question(query)

        # If it's a new question, reset the conversation history
        if is_new_question:
            self.user_histories[user_id] = self._get_default_user_history()

        # Appending the user's messages in history 
        self.user_histories[user_id].append({"role": "user", "content": query})

        try:
            # Sending requests to OpenAI via Azure
            chat_response = openai.ChatCompletion.create(
                engine=AZURE_OPENAI_DEPLOYMENT, 
                messages=self.user_histories[user_id]
            )

            # Fetching the answer and transferring it to Discord 
            chat_message = chat_response["choices"][0]["message"]["content"]

            # Edit the "thinking" message to the final response
            await thinking_message.edit(content=chat_message)

            # Appending the AI's answer in the history (list)
            self.user_histories[user_id].append({"role": "assistant", "content": chat_message})

            # Limiting the history's length to not exceed the token limit
            if len(self.user_histories[user_id]) > 10:  # Adjusting the maximum messages (if needed) 
                self.user_histories[user_id] = self.user_histories[user_id][-10:]

        except Exception as e:
            print(f"❌ Error during API-call: {str(e)}")
            await message.channel.send("❌ Jag stötte på ett fel. Försök igen senare.")

        await self.process_commands(message)

    def _is_new_question(self, query):
        """
        Determine if the user is asking a new question.
        This includes checking for keywords and code blocks.
        """
        # Keywords that indicate a new question
        new_question_keywords = ["how do I", "what is", "can you help", "explain", "help me", "new problem", "?"]
        
        # Check if the query contains any of the new question keywords
        contains_keyword = any(keyword in query.lower() for keyword in new_question_keywords)
        
        # Check if the query contains a code block (enclosed in triple backticks)
        contains_code_block = "```" in query
        
        # If either condition is met, treat it as a new question
        return contains_keyword or contains_code_block

# Starting the bot
async def main():
    bot = ChatGPTBot(command_prefix="!", intents=intents)
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())