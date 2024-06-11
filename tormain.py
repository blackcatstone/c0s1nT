import discord
from discord.ext import commands
import os
import shutil
from bs4 import BeautifulSoup
import sqlite3
import asyncio
import subprocess

# 디스코드 봇 설정
TOKEN = 'your token'
ALLOWED_GUILD_ID = 1244606106341347423
ALLOWED_CHANNEL_ID = 1245194709337374772

# intents 설정
intents = discord.Intents.default()
intents.messages = True  # 메시지 관련 이벤트 허용
intents.message_content = True  # 메시지 내용 읽기 허용

# 봇 명령어 접두사 설정 및 intents 추가
bot = commands.Bot(command_prefix='!', intents=intents)

# .txt 파일을 .html 파일로 변경하는 함수
def rename_txt_to_html(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            new_filename = filename.replace('.txt', '.html')
            shutil.move(os.path.join(directory, filename), os.path.join(directory, new_filename))

# 데이터베이스 파일 경로
db_file = 'data.db'
path_db_file = 'paths.db'

# 데이터베이스 초기화 및 테이블 생성
def initialize_database():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards_h1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        header TEXT,
        title TEXT,
        url TEXT,
        text TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards_h2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        header TEXT,
        name TEXT,
        url TEXT,
        date TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards_h3 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        header TEXT,
        title TEXT,
        url TEXT,
        text TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS paths (
        user_id INTEGER PRIMARY KEY,
        tor_path TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

# 데이터베이스에 데이터 추가
def add_card(header, title, url, text, table='cards_h1'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO {table} (header, title, url, text) VALUES (?, ?, ?, ?)
    ''', (header, title, url, text))
    conn.commit()
    conn.close()

def add_card_h2(header, name, url, date, table='cards_h2'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO {table} (header, name, url, date) VALUES (?, ?, ?, ?)
    ''', (header, name, url, date))
    conn.commit()
    conn.close()

def add_card_h3(header, title, url, text, table='cards_h3'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO {table} (header, title, url, text) VALUES (?, ?, ?, ?)
    ''', (header, title, url, text))
    conn.commit()
    conn.close()

def set_user_path(user_id, tor_path):
    conn = sqlite3.connect(path_db_file)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO paths (user_id, tor_path) VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET tor_path=excluded.tor_path
    ''', (user_id, tor_path))
    conn.commit()
    conn.close()

def get_user_path(user_id):
    conn = sqlite3.connect(path_db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT tor_path FROM paths WHERE user_id=?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

# 기존 데이터베이스 데이터를 가져오는 함수
def get_existing_data(table):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    if table == 'cards_h2':
        cursor.execute(f'SELECT header, name, url, date FROM {table}')
    else:
        cursor.execute(f'SELECT header, title, url, text FROM {table}')
    data = cursor.fetchall()
    conn.close()
    return data

# 데이터 비교 및 업데이트 함수
def compare_and_update_data(header, title_or_name, url, text_or_date, table):
    existing_data = get_existing_data(table)
    new_data = (header, title_or_name, url, text_or_date)
    if new_data not in existing_data:
        if table == 'cards_h2':
            add_card_h2(header, title_or_name, url, text_or_date, table)
        elif table == 'cards_h3':
            add_card_h3(header, title_or_name, url, text_or_date, table)
        else:
            add_card(header, title_or_name, url, text_or_date, table)
        print(f"Data updated in {table}")
        return True
    return False

# HTML 파일 파싱 및 데이터베이스에 저장
def parse_and_store_html_h1(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')

    wrapper = soup.find('div', id='wrapper')
    header = wrapper.find('h2').text.strip() if wrapper and wrapper.find('h2') else 'No Header'

    cards = soup.find_all('div', class_='card')
    updated = False
    for card in cards:
        title_elem = card.find('div', class_='title')
        url_elem = card.find('div', class_='url')
        text_elem = card.find('div', class_='text')

        title = title_elem.text.strip() if title_elem else 'No Title'
        url = url_elem.find('a')['href'] if url_elem and url_elem.find('a') else 'No URL'
        text = ' '.join([p.text.strip() for p in text_elem.find_all('p')]) if text_elem else 'No Text'

        if compare_and_update_data(header, title, url, text, 'cards_h1'):
            updated = True
    return updated

# HTML 파일 파싱 및 데이터베이스에 저장
def parse_and_store_html_h2(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')

    header_text = "No Header"
    content_div = soup.find('div', class_='content')
    if content_div:
        header = content_div.find('header')
        if header:
            main_div = header.find('div', class_='main')
            if main_div:
                link = main_div.find('a')
                header_text = link.text.strip() if link else 'No Text'

    posts = soup.find_all('li', class_='post')
    updated = False
    for post in posts:
        name_elem = post.find('a')
        date_elem = post.find('span', class_='meta')

        name = name_elem.text.strip() if name_elem else 'No Name'
        url = name_elem['href'] if name_elem and 'href' in name_elem.attrs else 'No URL'
        date = date_elem.text.strip() if date_elem else 'No Date'

        if compare_and_update_data(header_text, name, url, date, 'cards_h2'):
            updated = True
    return updated

def parse_and_store_html_h3(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')

    header_text = "No Header"
    wrapper = soup.find('div', class_='container h-100')
    if wrapper:
        header = wrapper.find('div', class_='col')
        header_text = header.text.strip() if header else 'No Header'

    cards = soup.find_all('div', class_='post-list')
    updated = False
    for card in cards:
        title_elem = card.find('div', class_='post-title-block')
        text_elem = card.find('div', class_='post-body')
        
        title = title_elem.text.strip() if title_elem else 'No Title'
        url = title_elem.find('div', class_='post-header').text.strip() if title_elem and title_elem.find('div', class_='post-header') else ''
        text = text_elem.text.strip() if text_elem else 'No Text'

        if compare_and_update_data(header_text, title, url, text, 'cards_h3'):
            updated = True
    return updated

# 정기적으로 HTML 파일을 파싱하여 데이터베이스에 저장하는 작업
async def scheduled_task():
    directory_path = 'C:\\Users\\whdwns\\Desktop\\tortext'
    rename_txt_to_html(directory_path)
    
    updated_h1 = parse_and_store_html_h1('C:/Users/whdwns/Desktop/tortext/blacksuit.html')
    updated_h2 = parse_and_store_html_h2('C:/Users/whdwns/Desktop/tortext/bianlian.html')
    updated_h3 = parse_and_store_html_h3('C:/Users/whdwns/Desktop/tortext/threeamk.html')

    if updated_h1 or updated_h2 or updated_h3:
        channel = bot.get_channel(ALLOWED_CHANNEL_ID)
        if channel:
            await channel.send('데이터가 업데이트 되었습니다.')

async def scheduler():
    while True:
        await scheduled_task()
        await asyncio.sleep(60)  # 1분마다 실행

# 봇 명령어 설정 및 이벤트 핸들러
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    for guild in bot.guilds:
        print(f'Connected to guild: {guild.name} (ID: {guild.id})')

    # 봇이 특정 채널에 메시지를 보냅니다.
    channel = bot.get_channel(ALLOWED_CHANNEL_ID)
    if channel:
        await channel.send(
            'c0s1nT 봇이 성공적으로 로그인되었습니다!\n'
            '@6시간마다 시스템이 크롤링하여 정보를 업데이트하고 새로운 정보를 알림으로 보내드립니다.@\n'
            '다음은 사용법 안내입니다:\n'
            '- `!t <path>`: Tor 브라우저 경로를 설정합니다. 예시 (windows 기준) !t C:\\Users\\사용자이름\\Desktop\\Tor Browser\\Browser\\firefox.exe\n'
            '- `!h`: 첫 번째 HTML 데이터 black suit를 가져와 출력합니다.\n'
            '- `!h2`: 두 번째 HTML 데이터 BianLian를 가져와 출력합니다.\n'
            '- `!h3`: 세 번째 HTML 데이터를 threeAM를 가져와 출력합니다.\n'
            '사용 중 문제가 발생하면 관리자(도르 / hack.stone.cat)에게 문의하세요.'
        )

    # 스케줄러 시작
    bot.loop.create_task(scheduler())

# Tor 브라우저 경로 설정 명령어
@bot.command()
async def t(ctx, *, path: str = None):
    if path is None:
        await ctx.send(r'경고: Tor 브라우저 경로가 설정되지 않았습니다. 사용법: !t <path_to_tor_browser>')
        return

    user_id = ctx.author.id
    set_user_path(user_id, path)
    await ctx.send(f'Tor 브라우저 경로가 설정되었습니다: {path}')

# Tor 브라우저로 .onion 링크 열기 함수
def open_onion_url(user_id, onion_url):
    tor_path = get_user_path(user_id)
    if tor_path:
        try:
            subprocess.Popen([tor_path, onion_url])
            return True
        except Exception as e:
            print(f"Error opening Tor browser: {e}")
            return False
    else:
        return False

# HTML 데이터 읽기 명령어
@bot.command()
async def h(ctx):
    try:
        # 파일 경로 설정
        file_path = 'C:/Users/whdwns/Desktop/tortext/blacksuit.html'

        # 로컬 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(content, 'html.parser')

        # <div id="wrapper"> 내의 <h2> 태그 텍스트 추출
        wrapper = soup.find('div', id='wrapper')
        header = wrapper.find('h2').text.strip() if wrapper and wrapper.find('h2') else 'No Header'

        # 첫 번째 카드의 정보를 추출하여 메시지 작성
        card = soup.find('div', class_='card')
        if card:
            title_elem = card.find('div', class_='title')
            url_elem = card.find('div', class_='url')
            text_elem = card.find('div', class_='text')

            title = title_elem.text.strip() if title_elem else 'No Title'
            url = url_elem.find('a')['href'] if url_elem and url_elem.find('a') else 'No URL'
            text = ' '.join([p.text.strip() for p in text_elem.find_all('p')]) if text_elem else 'No Text'

            # Tor 브라우저로 열릴 .onion 링크
            onion_url = 'http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion/'

            # 디스코드 메시지 작성
            notification = f"**{header}**\n\n**{title}**\n\n[Website]({url})\n\n{text}\n"

            # 너무 긴 경우 일부만 출력
            if len(notification) > 2000:
                notification = notification[:2000] + '...'

            await ctx.send(notification)

            # .onion 링크를 Tor 브라우저로 열기
            if open_onion_url(ctx.author.id, onion_url):
                await ctx.send(f".onion 링크를 Tor 브라우저로 여는 중: {onion_url}")
            else:
                await ctx.send("Tor 브라우저 경로가 설정되지 않았거나 실행하는 중에 오류가 발생했습니다.")

            # 데이터 업데이트 여부 확인
            updated_h1 = parse_and_store_html_h1(file_path)
            if updated_h1:
                await ctx.send('데이터가 업데이트 되었습니다.')
        else:
            await ctx.send('No card found.')
    except Exception as e:
        await ctx.send(f'Failed to read the HTML content. Error: {e}')

@bot.command()
async def h2(ctx):
    try:
        # 파일 경로 설정
        file_path = 'C:/Users/whdwns/Desktop/tortext/bianlian.html'

        # 로컬 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(content, 'html.parser')

        # <div class="content"> 내의 <header> 태그 텍스트 추출
        content_div = soup.find('div', class_='content')
        header = content_div.find('header').text.strip() if content_div and content_div.find('header') else 'No Header'

        # 첫 번째 카드의 정보를 추출하여 메시지 작성
        card = soup.find('li', class_='post')
        if card:
            name_elem = card.find('a')
            date_elem = card.find('span', class_='meta')

            name = name_elem.text.strip() if name_elem else 'No Name'
            url = name_elem['href'] if name_elem and 'href' in name_elem.attrs else 'No URL'
            date = date_elem.text.strip() if date_elem else 'No Date'

            # Tor 브라우저로 열릴 .onion 링크
            onion_url = 'http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/companies'

            # 디스코드 메시지 작성
            notification = f"**{header}**\n\n**{name}**\n\n[Website]({url})\n\n{date}\n"

            # 너무 긴 경우 일부만 출력
            if len(notification) > 2000:
                notification = notification[:2000] + '...'

            await ctx.send(notification)

            # .onion 링크를 Tor 브라우저로 열기
            if open_onion_url(ctx.author.id, onion_url):
                await ctx.send(f".onion 링크를 Tor 브라우저로 여는 중: {onion_url}")
            else:
                await ctx.send("Tor 브라우저 경로가 설정되지 않았거나 실행하는 중에 오류가 발생했습니다.")

            # 데이터 업데이트 여부 확인
            updated_h2 = parse_and_store_html_h2(file_path)
            if updated_h2:
                await ctx.send('데이터가 업데이트 되었습니다.')
        else:
            await ctx.send('No post found.')
    except Exception as e:
        await ctx.send(f'Failed to read the HTML content. Error: {e}')

@bot.command()
async def h3(ctx):
    try:
        # 파일 경로 설정
        file_path = 'C:/Users/whdwns/Desktop/tortext/threeamk.html'

        # 로컬 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(content, 'html.parser')

        # <div class="container h-100"> 내의 <div class="col"> 태그 텍스트 추출
        wrapper = soup.find('div', class_='container h-100')
        header = wrapper.find('div', class_='col').text.strip() if wrapper and wrapper.find('div', class_='col') else 'No Header'

        # 첫 번째 카드의 정보를 추출하여 메시지 작성
        card = soup.find('div', class_='post-list')
        if card:
            title_elem = card.find('div', class_='post-title-block')
            text_elem = card.find('div', class_='post-body')

            title = title_elem.text.strip() if title_elem else 'No Title'
            url = title_elem.find('div', class_='post-header').text.strip() if title_elem and title_elem.find('div', class_='post-header') else 'No URL'
            text = text_elem.text.strip() if text_elem else 'No Text'

            # Tor 브라우저로 열릴 .onion 링크
            onion_url = 'http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion/companies'

            # 디스코드 메시지 작성
            notification = f"**{header}**\n\n**{title}**\n\n[Website]({url})\n\n{text}\n"

            # 너무 긴 경우 일부만 출력
            if len(notification) > 2000:
                notification = notification[:2000] + '...'

            await ctx.send(notification)

            # .onion 링크를 Tor 브라우저로 열기
            if open_onion_url(ctx.author.id, onion_url):
                await ctx.send(f".onion 링크를 Tor 브라우저로 여는 중: {onion_url}")
            else:
                await ctx.send("Tor 브라우저 경로가 설정되지 않았거나 실행하는 중에 오류가 발생했습니다.")

            # 데이터 업데이트 여부 확인
            updated_h3 = parse_and_store_html_h3(file_path)
            if updated_h3:
                await ctx.send('데이터가 업데이트 되었습니다.')
        else:
            await ctx.send('No card found.')
    except Exception as e:
        await ctx.send(f'Failed to read the HTML content. Error: {e}')

# 봇 실행
if __name__ == "__main__":
    initialize_database()
    bot.run(TOKEN)
