# IMPORTERA BIBLIOTEK
import os
from dotenv import load_dotenv
import openai
import discord
from discord.ext import commands
import asyncio

# Ladda miljövariabler från .env-filen
load_dotenv()

# Discord intents (vad botten har tillgång till)
intents = discord.Intents.default()
intents.message_content = True

# API-nycklar och endpoints
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT") 
OPENAI_API_VERSION = "2024-07-01-preview"

# Konfigurera Azure OpenAI API
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_version = OPENAI_API_VERSION

# Discord bot-klass
class ChatGPTBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.message_history = []  # Historik för att behålla kontext

    async def on_ready(self):
        print(f"✅ {self.user} är nu online och redo att svara!")

    async def on_message(self, message):
        if message.author == self.user:
            return  # Ignorera botens egna meddelanden

        query = message.content

        # Skapa systemprompt
        self.message_history = [
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
                ),
            },
            {"role": "user", "content": query},
        ]

        try:
            # Skicka förfrågan till OpenAI via Azure
            chat_response = openai.ChatCompletion.create(
                engine=AZURE_OPENAI_DEPLOYMENT, 
                messages=self.message_history
            )

            # Hämta svaret och skicka det till Discord
            chat_message = chat_response["choices"][0]["message"]["content"]
            await message.channel.send(chat_message)

            # Spara historik
            self.message_history.append({"role": "assistant", "content": chat_message})

        except Exception as e:
            print(f"❌ Fel vid API-anrop: {str(e)}")
            await message.channel.send("❌ Jag stötte på ett fel. Försök igen senare.")

        await self.process_commands(message)

# Starta botten
async def main():
    bot = ChatGPTBot(command_prefix="!", intents=intents)
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
