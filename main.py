import asyncio
import aiohttp
import os
from telethon import TelegramClient, events

# Config from environment variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
PHONE = os.environ.get("PHONE")
N8N_WEBHOOK = os.environ.get("N8N_WEBHOOK")

# Keywords
SEO_KEYWORDS = [
    'seo', 'need seo', 'seo help', 'looking for seo', 'hire seo',
    'seo agency', 'seo specialist', 'seo consultant', 'seo recommendations',
    'not showing up on google', 'google not indexing', 'lost rankings',
    'rank on google', 'website traffic', 'no traffic', 'backlink',
    'domain authority', 'technical seo', 'seo audit', 'content marketing',
    'search engine', 'keyword research', 'serp', 'google penalty',
    'competitors ranking', 'outrank', 'page speed seo', 'link building',
    'потрібен seo', 'шукаю seo', 'seo фахівець', 'просування сайту',
    'виведення в топ', 'органічний трафік', 'індексація сайту',
    'позиції в гугл', 'seo спеціаліст', 'потрібне просування',
    'нема трафіку', 'сайт не знаходять', 'впав трафік'
]

WEB3_KEYWORDS = [
    'web3', 'blockchain', 'solidity', 'smart contract', 'dapp',
    'defi', 'nft', 'dao', 'crypto', 'token', 'layer2', 'erc-20',
    'erc20', 'hire blockchain', 'hire web3', 'need web3', 'web3 developer',
    'blockchain developer', 'web3 team', 'blockchain development',
    'nft marketplace', 'defi protocol', 'token development',
    'smart contract audit', 'web3 outsource', 'blockchain mvp',
    'crypto startup', 'custom blockchain', 'web3 product',
    'потрібен web3', 'блокчейн розробник', 'смарт контракт',
    'крипто проект', 'web3 команда', 'блокчейн проект',
    'токен розробка', 'nft розробка', 'defi розробка'
]

# Chats to monitor
CHATS = [
    'chat_targetologov', 'smmbunker', 'theinstapreneurscommunity',
    'go_motion_ua', 'target_tricks', 'tiktoktarget_chat',
    'ukraine_digital', 'community_EdTech', 'sendpulseacademy',
    'hworknet_community', 'digitaltopchik', 'notabenebusiness',
    'kyivdigitalpochik', 'Ukr_copywriters_group', 'ua_wp',
    'executive_search_ua', 'spaceberry_community', 'huntlify',
    'vizual_hub', 'marketing_jobs_ua', 'salesheroadschat',
    'it_job_ua', 'itexpert_vacancies', 'webflow_ukraine',
    'sales_jobs_ua', 'top_vacansii', 'premium_job_ua',
    'freelance247', 'PRO_Design_chat_PSS', 'HR_IT_Community_chat',
    'kol3io', 'OfficialCryptoExpoDubai', 'w3xnetwork',
    'VCsDAO', 'SV_founders', 'CryptoHorizonEverywhere',
    'buildondogeos', 'myronairdropchat',
    # invite links — потрібно вступити вручну заздалегідь
    # потім додати їх username або chat_id сюди
]

client = TelegramClient('leadmonitor', API_ID, API_HASH)

def categorize(text):
    text_lower = text.lower()
    is_web3 = any(kw in text_lower for kw in WEB3_KEYWORDS)
    is_seo = any(kw in text_lower for kw in SEO_KEYWORDS)
    if is_web3:
        return 'web3'
    if is_seo:
        return 'seo'
    return None

async def send_to_n8n(data):
    async with aiohttp.ClientSession() as session:
        await session.post(N8N_WEBHOOK, json=data)

@client.on(events.NewMessage(chats=CHATS))
async def handler(event):
    text = event.message.text or ''
    category = categorize(text)
    if not category:
        return

    sender = await event.get_sender()
    chat = await event.get_chat()

    username = getattr(sender, 'username', None) or 'no_username'
    first_name = getattr(sender, 'first_name', '') or ''
    last_name = getattr(sender, 'last_name', '') or ''
    chat_title = getattr(chat, 'title', '') or ''
    chat_username = getattr(chat, 'username', '') or ''

    profile_link = f"https://t.me/{username}" if username != 'no_username' else 'no link'
    chat_link = f"https://t.me/{chat_username}" if chat_username else 'private group'

    payload = {
        'category': category,
        'text': text[:500],
        'sender_name': f"{first_name} {last_name}".strip(),
        'sender_username': username,
        'profile_link': profile_link,
        'chat_title': chat_title,
        'chat_link': chat_link,
        'message_link': f"{chat_link}/{event.message.id}" if chat_username else 'private'
    }

    await send_to_n8n(payload)
    print(f"[{category.upper()}] {chat_title} | {first_name}: {text[:80]}")

async def main():
    await client.start(phone=PHONE)
    print("Userbot started! Monitoring chats...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
