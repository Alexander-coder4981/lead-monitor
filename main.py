import asyncio
import aiohttp
import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
N8N_WEBHOOK = os.environ.get("N8N_WEBHOOK")
SESSION_STRING = os.environ.get("SESSION_STRING")

# Короткі слова — перевіряємо як цілі слова (word boundary)
WEB3_EXACT = [
    'web3', 'nft', 'dao', 'defi', 'dapp', 'crypto',
    'токен', 'крипта', 'криптo'
]

# Довгі фрази — перевіряємо як підрядок
WEB3_PARTIAL = [
    # Розробка
    'blockchain', 'solidity', 'smart contract', 'layer2', 'erc-20', 'erc20',
    'web3 developer', 'blockchain developer', 'solidity developer',
    'smart contract developer', 'blockchain development', 'web3 development',
    'web3 team', 'web3 outsource', 'blockchain mvp', 'web3 product',
    'hire blockchain', 'hire web3', 'need web3',
    # Продукти
    'nft marketplace', 'defi protocol', 'token development', 'tokenomics',
    'smart contract audit', 'crypto startup', 'custom blockchain',
    'crypto exchange', 'crypto wallet', 'crypto project',
    'web3 app', 'decentralized app', 'defi app', 'blockchain app',
    'p2e', 'play to earn', 'gamefi', 'metaverse development',
    # Інфра
    'ethereum', 'solana', 'polygon', 'binance smart chain', 'bsc',
    'avalanche', 'near protocol', 'polkadot', 'substrate',
    'hardhat', 'foundry', 'truffle', 'web3.js', 'ethers.js',
    'ipfs', 'chainlink', 'opensea',
    # Укр/рос
    'блокчейн розробник', 'смарт контракт', 'крипто проект',
    'web3 команда', 'блокчейн проект', 'токен розробка',
    'nft розробка', 'defi розробка', 'потрібен web3',
    'блокчейн розробка', 'крипто стартап', 'децентралізований',
    'криптовалют', 'майнінг сайт', 'крипто біржа',
]

# Короткі SEO слова
SEO_EXACT = [
    'seo', 'serp', 'sem', 'ppc',
]

# Довгі SEO фрази
SEO_PARTIAL = [
    # Прямий запит
    'need seo', 'seo help', 'looking for seo', 'hire seo',
    'seo agency', 'seo specialist', 'seo consultant', 'seo expert',
    'seo recommendations', 'seo service', 'seo manager',
    'seo freelancer', 'seo підрядник', 'seo на аутсорс',
    # Проблеми з сайтом
    'not showing up on google', 'google not indexing',
    'lost rankings', 'site dropped', 'ranking dropped',
    'penalty recovery', 'google penalty', 'manual action google',
    'website not found', "can't find my site",
    'не індексується', 'сайт не знаходять', 'впав трафік',
    'не показується в гугл', 'вилетів з гугла',
    # Трафік
    'rank on google', 'website traffic', 'organic traffic',
    'no traffic', 'increase traffic', 'get more visitors',
    'виведення в топ', 'органічний трафік', 'нема трафіку',
    'позиції в гугл', 'топ гугл', 'перша сторінка гугл',
    # Технічне
    'backlink', 'link building', 'domain authority',
    'technical seo', 'seo audit', 'page speed seo',
    'core web vitals', 'sitemap', 'robots.txt проблема',
    'індексація сайту', 'технічне seo',
    # Конкуренти
    'competitors ranking', 'outrank competitors',
    'конкуренти вище в гугл', 'обігнати конкурентів в гугл',
    # Контент
    'content marketing', 'keyword research', 'search engine',
    'blog for seo', 'seo content', 'write for seo',
    'контент під seo', 'seo тексти', 'ключові слова сайт',
    # Локальне seo
    'local seo', 'google maps ranking', 'google my business',
    'google business profile', 'локальне seo', 'гугл мапи просування',
    # Загальне
    'потрібен seo', 'шукаю seo', 'seo фахівець',
    'просування сайту', 'seo спеціаліст', 'потрібне просування',
    'розкрутка сайту', 'просування в пошуку',
    # Реклама (суміжне)
    'google ads specialist', 'google ads help', 'ppc specialist',
    'контекстна реклама', 'гугл реклама фахівець',
]

CHATS = [
    'chat_targetologov', 'smmbunker', 'theinstapreneurscommunity',
    'go_motion_ua', 'target_tricks', 'tiktoktarget_chat',
    'ukraine_digital', 'community_EdTech', 'sendpulseacademy',
    'hworknet_community', 'digitaltopchik', 'notabenebusiness',
    'kyivdigitaltopchik', 'Ukr_copywriters_group', 'ua_wp',
    'executive_search_ua', 'spaceberry_community', 'huntlify',
    'vizual_hub', 'marketing_jobs_ua', 'salesheroadschat',
    'it_job_ua', 'itexpert_vacancies', 'webflow_ukraine',
    'sales_jobs_ua', 'top_vacansii', 'premium_job_ua',
    'freelance247', 'PRO_Design_chat_PSS', 'HR_IT_Community_chat',
    'kol3io', 'OfficialCryptoExpoDubai', 'w3xnetwork',
    'VCsDAO', 'SV_founders', 'CryptoHorizonEverywhere',
    'buildondogeos', 'myronairdropchat', 'doshkajob',
    'graphic_designerisss_chat', 'affhub_community', 'RudenkoSMM',
    'emontajka', 'PRO_Ecommerce_chat', 'real_targetolog', 'ua_ugc_chat',
]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def categorize(text):
    text_lower = text.lower()

    is_web3 = any(
        re.search(r'\b' + re.escape(kw) + r'\b', text_lower)
        for kw in WEB3_EXACT
    ) or any(kw in text_lower for kw in WEB3_PARTIAL)

    is_seo = any(
        re.search(r'\b' + re.escape(kw) + r'\b', text_lower)
        for kw in SEO_EXACT
    ) or any(kw in text_lower for kw in SEO_PARTIAL)

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
    chat_title = getattr(chat, 'title', '') or ''
    chat_username = getattr(chat, 'username', '') or ''
    profile_link = f"https://t.me/{username}" if username != 'no_username' else 'no link'
    chat_link = f"https://t.me/{chat_username}" if chat_username else 'private group'

    payload = {
        'category': category,
        'text': text[:500],
        'sender_name': first_name,
        'sender_username': username,
        'profile_link': profile_link,
        'chat_title': chat_title,
        'chat_link': chat_link,
        'source': 'telegram'
    }

    await send_to_n8n(payload)
    print(f"[{category.upper()}] {chat_title} | {first_name}: {text[:80]}")

async def main():
    await client.connect()
    print("Userbot started! Monitoring chats...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
