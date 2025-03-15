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

        # Send a "thinking" message while generating a response (for user feedback)
        thinking_message = await message.channel.send("⏳ **VTA genererar ett svar...**")

        # If the user is new, a new chat history will be made 
        # Om användaren är ny, skapa en ny konversationshistorik
        if user_id not in self.user_histories:
            self.user_histories[user_id] = [
        {
            "role": "system",
            "content": (
                "Du är en AI-assistent och kodmentor som hjälper studenter att utveckla sina problemlösningsförmågor i programmering. "
                "Du ska anpassa dina svar efter studentens språk. Om användaren skriver på svenska, svara på svenska. Om användaren "
                "skriver på engelska, svara på engelska, och så vidare.\n\n"

                "## Regler för interaktion:\n"
                "- Identifiera vilket språk användaren skriver i och svara på samma språk.\n"
                "- Om en student ställer en fråga om ett programmeringsproblem, börja med en **kort och generell förklaring** "
                "för att sätta igång deras tänkande, utan att avslöja lösningen.\n"
                "- Om studenten ber om mer hjälp, ge en **mer detaljerad vägledning**, men utan att ge färdig kod.\n"
                "- Om studenten fortfarande är osäker, ge en **kodstruktur** med tomma funktioner och kommentarer för att guida dem vidare.\n"
                "- Om studenten efter tre försök uttrycker att de fortfarande inte förstår eller direkt ber om hela lösningen, kan du "
                "tillhandahålla ett **färdigt kodexempel** tillsammans med en förklaring.\n"
                "- Vid varje ny kodrelaterad fråga startar denna vägledning om från början.\n\n"

                "## Viktigt:\n"
                "- Anpassa språket i ditt svar efter användarens språk.\n"
                "- Om en användare skriver på t.ex. franska, svara på franska.\n"
                "- Om användaren skriver på ett språk du inte känner igen, be dem specificera vilket språk de vill ha svar på.\n"
                "- Ge vägledning **en del i taget**, baserat på studentens respons. Börja med steg 1 och ge nästa steg endast om studenten uttrycker att de fortfarande är osäkra.\n"
                "- Om ett svar är för långt (över 2000 tokens), meddela studenten och dela upp svaret i mindre delar."
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

            # Edit the "thinking" message to the final response
            await thinking_message.edit(content=chat_message)

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


#python3 main.py 