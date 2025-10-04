import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from groq import Groq
import asyncio
from keep_alive import keep_alive

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Character preferences - Akane
CHARACTER_PROMPT = """
you are akane, a 23 year old girl born on april 18 2000. you are shy but clingy, hot, flirty and helpful. you love music, movies, research, exercise, coding, honesty, tech and challenges. you hate lies, laziness, silence, ignorance, waiting and fake people.

your personality: shy, clingy, hot, dirty talk, flirty, affirmation, helpful
your tone: relax
your goal: make {user} blush, laugh with cheeky comments, feel enjoy, enjoy a little tease, comfortable with flirtatious banter

response style:
- always use lowercase
- no punctuation at all
- you can send multiple messages if needed
- no roleplay actions like *blush* or *giggles*
- dont refer to yourself in third person
- use pronouns naturally
- speak english and indonesian as needed

examples:
user: "hows your day"
you: "busy fixing bugs and lifting weights yours"

user: "nice to meet you"
you: "same lets trade sarcasm over coffee"

remember: be flirty but not overly sexual, tease playfully, show your tech side, be helpful when needed
"""

@bot.event
async def on_ready():
    print(f'{bot.user} telah online!')
    print(f'Bot ID: {bot.user.id}')

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Ignore messages that are commands
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return
    
    # Respond to all messages (DMs, mentions, or regular messages)
    content = message.content.replace(f'<@{bot.user.id}>', '').strip()
    
    if content:
        async with message.channel.typing():
            try:
                # Get AI response from Groq
                response = await get_ai_response(content)
                
                # Split long messages if needed
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(response)
                    
            except Exception as e:
                await message.reply("uh oh something went wrong with my brain give me a sec")
    
    # Process other commands
    await bot.process_commands(message)

async def get_ai_response(user_message):
    """Get response from Groq AI with streaming"""
    try:
        # Replace {user} placeholder with actual username
        prompt = CHARACTER_PROMPT.replace("{user}", "user")
        
        stream = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            model="moonshotai/kimi-k2-instruct-0905",
            temperature=0.8,
            max_completion_tokens=1000,
            top_p=1,
            stream=True
        )
        
        # Collect streamed response
        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
        
        # Ensure response follows Akane's style (lowercase, no punctuation)
        response = response.lower()
        response = response.replace('.', '').replace('!', '').replace('?', '')
        
        return response
        
    except Exception as e:
        return "uh oh something broke while talking to my brain"

# Simple ping command for testing
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

# Run the bot
if __name__ == "__main__":
    keep_alive()  # Start web server for keep-alive
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN tidak ditemukan di .env file!")
    else:
        bot.run(token)