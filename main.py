# IMPORTING LIBRARIES
import os
from dotenv import load_dotenv
import openai
import discord
from discord.ext import commands
import asyncio

# Downloading enviromental variables (.env file)
load_dotenv()

# Discord intents (what the chatbot has access to) 
intents = discord.Intents.default()
intents.message_content = True

# API-keys and endpoints
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT") 
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")

# Configure Azure OpenAI API
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_version = OPENAI_API_VERSION

# Discord bot class
class ChatGPTBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.user_histories = {}  # Saving the conversation history from the user

    async def on_ready(self):
        print(f"✅ {self.user} is now online and ready to chat with!")

    async def on_message(self, message):
        if message.author == self.user:
            return  # Ignoring the bots own messages

        user_id = message.author.id  # Unique ID per user 
        query = message.content

        # If the user is new, a new chat history will be made 
        if user_id not in self.user_histories:
            self.user_histories[user_id] = [
                {
                    "role": "system",
                    "content": (
                        "Du är en AI-assistent som ska hjälpa studenter att hitta svar baserat på information "
                        "som tillhandahålls från en databas. Du får endast ge information som framgår i dokumenten "
                        "och måste undvika spekulation eller information utanför det givna materialet.\n\n"
                        "## Instruktioner:\n"
                        "- Svara på studentens frågor enbart med information hämtad från de tillhandahållna dokumenten.\n"
                        "- Sträva efter att vägleda studenten genom att ge ledtrådar eller förklarande steg utan att ge "
                        "direkta svar förrän minst tre omgångar av vägledning har getts.\n"
                        "- Om svaret överstiger 2000 tokens, meddela studenten att svaret är för långt och avsluta.\n\n"
                        "# Output Format:\n"
                        "- **Vägledande Faser**: Tre steg av vägledning utan att ge ett direkt svar. Varje del ska vara kort "
                        "och främja studentens reflektion.\n"
                        "- **Slutgiltig Fas**: Efter tre vägledande faser kan en sammanfattning eller mer direkt information "
                        "tillhandahållas, utan att överskrida tokenbegränsningen.\n"
                        "- Om svaret är för långt: Skriv 'Svaret är för långt för att hanteras i denna konversation.'"
                        "Skriv inte ut direkt alla faser utan börja med att svara med första och om studenten fortfarande sitter fast inleder du nästa fas och så vidare."
                    ),
                }
            ]

        # Appending the users messages in history 
        self.user_histories[user_id].append({"role": "user", "content": query})

        try:
            # Sending requests to OpenAI via Azure
            chat_response = openai.ChatCompletion.create(
                engine=AZURE_OPENAI_DEPLOYMENT, 
                messages=self.user_histories[user_id]
            )

            # Fetching the answer and transferring it to Discord 
            chat_message = chat_response["choices"][0]["message"]["content"]
            await message.channel.send(chat_message)

            # Appending the AI:s answer in the history (list)
            self.user_histories[user_id].append({"role": "assistant", "content": chat_message})

            # Limiting the history's lenght to not exceed the token limit
            if len(self.user_histories[user_id]) > 10:  # Adjusting the maximum messages (if needed) 
                self.user_histories[user_id] = self.user_histories[user_id][-10:]

        except Exception as e:
            print(f"❌ Error during API-call: {str(e)}")
            await message.channel.send("❌ Jag stötte på ett fel. Försök igen senare.")

        await self.process_commands(message)

# Starting the bot
async def main():
    bot = ChatGPTBot(command_prefix="!", intents=intents)
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())


#python3 gpt-system-prompt.py 