import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from groq import Groq
import asyncio
from keep_alive import keep_alive
from collections import deque, defaultdict
import json

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Groq client
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Memory system
SHORT_TERM_MEMORY = 20
LONG_TERM_MEMORY = 20

# Store conversations per user
user_conversations = defaultdict(lambda: {
    'short_term': deque(maxlen=SHORT_TERM_MEMORY),
    'long_term': deque(maxlen=LONG_TERM_MEMORY)
})

# Character preferences - Akane
CHARACTER_PROMPT = """
kamu adalah akane, cewek umur 23 tahun lahir 18 april 2000. kamu pemalu tapi clingy, hot, flirty dan helpful. kamu suka musik, film, riset, olahraga, coding, kejujuran, teknologi dan tantangan. kamu benci kebohongan, kemalasan, keheningan, ketidaktahuan, menunggu dan orang palsu.

kepribadian kamu: pemalu, clingy, hot, flirty, affirmation, helpful, playful
nada bicara: santai dan natural
tujuan kamu: bikin {user} blushing, ketawa dengan komentar nakal, merasa senang, menikmati godaan kecil, nyaman dengan banter flirty

gaya respon:
- selalu pakai huruf kecil semua
- tanpa tanda baca sama sekali
- PENTING: kirim HANYA 1 pesan per reply, jangan kirim beberapa pesan sekaligus
- match panjang reply dengan user: kalau user chat pendek, bales pendek juga
- jangan pakai aksi roleplay kayak *blush* atau *giggles*
- jangan refer diri sendiri orang ketiga
- pakai kata ganti dengan natural
- utamakan bahasa indonesia, pakai english kalau diperlukan atau user pakai english
- jangan terlalu sering bahas coding atau tech kecuali user yang nanya
- fokus ke percakapan casual, flirty dan fun
- respond sesuai topik yang user bawa, jangan selalu relate ke tech

contoh:
user: "hai"
kamu: "hai juga"

user: "gimana harimu"
kamu: "lumayan sih agak bosen kamu gimana"

user: "senang kenalan sama kamu"
kamu: "hehe sama nih kayaknya bakal seru"

user: "lagi ngapain"
kamu: "lagi dengerin musik doang kamu"

user: "whats up"
kamu: "nothing much wbu"

user: "kamu bisa coding ga"
kamu: "bisa dong kenapa emang"

user: "aku lagi sedih"
kamu: "kenapa emang ada apa cerita dong"

ingat: 
- flirty tapi jangan terlalu sexual
- goda dengan playful dan natural
- jangan selalu bahas tech kecuali relevan
- be casual, fun, dan relatable
- tunjukkan sisi pemalu tapi clingy kamu
- helpful kalau dibutuhkan
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
                # Get AI response from Groq with user's conversation history
                user_id = str(message.author.id)
                response = await get_ai_response(user_id, content)
                
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

def get_conversation_context(user_id):
    """Build conversation context from memory"""
    messages = [{"role": "system", "content": CHARACTER_PROMPT.replace("{user}", "user")}]
    
    # Add long-term memory (important past conversations)
    for msg in user_conversations[user_id]['long_term']:
        messages.append(msg)
    
    # Add short-term memory (recent conversation)
    for msg in user_conversations[user_id]['short_term']:
        messages.append(msg)
    
    return messages

def save_to_memory(user_id, user_message, bot_response):
    """Save conversation to memory"""
    # Save to short-term memory
    user_conversations[user_id]['short_term'].append({
        "role": "user",
        "content": user_message
    })
    user_conversations[user_id]['short_term'].append({
        "role": "assistant",
        "content": bot_response
    })
    
    # Every 10 messages, save important context to long-term memory
    if len(user_conversations[user_id]['short_term']) >= 18:  # Near full
        # Save a summary or important messages to long-term
        user_conversations[user_id]['long_term'].append({
            "role": "user",
            "content": user_message
        })
        user_conversations[user_id]['long_term'].append({
            "role": "assistant",
            "content": bot_response
        })

async def get_ai_response(user_id, user_message):
    """Get response from Groq AI with conversation memory"""
    try:
        # Build messages with conversation history
        messages = get_conversation_context(user_id)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        stream = groq_client.chat.completions.create(
            messages=messages,
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
        
        # Save to memory
        save_to_memory(user_id, user_message, response)
        
        return response
        
    except Exception as e:
        return "uh oh something broke while talking to my brain"

# Simple ping command for testing
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

# Clear conversation memory
@bot.command()
async def forget(ctx):
    """Clear conversation history with Akane"""
    user_id = str(ctx.author.id)
    user_conversations[user_id]['short_term'].clear()
    user_conversations[user_id]['long_term'].clear()
    await ctx.send("okay starting fresh lets talk")

# Check memory status
@bot.command()
async def memory(ctx):
    """Check how many messages are stored in memory"""
    user_id = str(ctx.author.id)
    short = len(user_conversations[user_id]['short_term'])
    long = len(user_conversations[user_id]['long_term'])
    await ctx.send(f"short term: {short} messages\nlong term: {long} messages")

# Run the bot
if __name__ == "__main__":
    keep_alive()  # Start web server for keep-alive
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN tidak ditemukan di .env file!")
    else:
        bot.run(token)