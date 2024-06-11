import sqlite3
from bs4 import BeautifulSoup
import os
import shutil
import sys
import io

# UTF-8 인코딩을 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# .txt 파일을 .html 파일로 변경하는 함수
def rename_txt_to_html(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            new_filename = filename.replace('.txt', '.html')
            shutil.move(os.path.join(directory, filename), os.path.join(directory, new_filename))

# 데이터베이스 초기화 및 테이블 생성
def initialize_database():
    conn = sqlite3.connect('data.db')
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
    conn.commit()
    conn.close()
    print("Database initialized.")

# 데이터베이스에 데이터 추가
def add_card(header, title, url, text, table='cards'):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO {table} (header, title, url, text) VALUES (?, ?, ?, ?)
    ''', (header, title, url, text))
    conn.commit()
    conn.close()

def add_card_h2(header, name, url, date, table='cards_h2'):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO {table} (header, name, url, date) VALUES (?, ?, ?, ?)
    ''', (header, name, url, date))
    conn.commit()
    conn.close()
    print(f"Added to {table}: header={header}, name={name}, url={url}, date={date}")

def add_card_h3(header, title, url, text, table='cards_h3'):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO {table} (header, title, url, text) VALUES (?, ?, ?, ?)
    ''', (header, title, url, text))
    conn.commit()
    conn.close()
    print(f"Added to {table}: header={header}, title={title}, url={url}, text={text}")

# 기존 데이터베이스 데이터를 가져오는 함수
def get_existing_data(table):
    conn = sqlite3.connect('data.db')
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
def parse_and_store_html_h(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(f"File {file_path} read successfully.")
    
    soup = BeautifulSoup(content, 'html.parser')

    wrapper = soup.find('div', id='wrapper')
    header = wrapper.find('h2').text.strip() if wrapper and wrapper.find('h2') else 'No Header'

    cards = soup.find_all('div', class_='card')
    for card in cards:
        title_elem = card.find('div', class_='title')
        url_elem = card.find('div', class_='url')
        text_elem = card.find('div', class_='text')

        title = title_elem.text.strip() if title_elem else 'No Title'
        url = url_elem.find('a')['href'] if url_elem and url_elem.find('a') else 'No URL'
        text = text_elem.text.strip() if text_elem else 'No Text'

        compare_and_update_data(header, title, url, text, 'cards_h1')

# HTML 파일 파싱 및 데이터베이스에 저장
def parse_and_store_html_h2(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(f"File {file_path} read successfully.")
    
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
                print(f"Parsed header text: {header_text}")

    # ul.posts 내의 li.post 요소를 찾습니다.
    posts = soup.find_all('li', class_='post')
    for post in posts:
        name_elem = post.find('a')
        date_elem = post.find('span', class_='meta')

        name = name_elem.text.strip() if name_elem else 'No Name'
        url = name_elem['href'] if name_elem and 'href' in name_elem.attrs else 'No URL'
        date = date_elem.text.strip() if date_elem else 'No Date'

        compare_and_update_data(header_text, name, url, date, 'cards_h2')

def parse_and_store_html_h3(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(f"File {file_path} read successfully.")
    
    soup = BeautifulSoup(content, 'html.parser')

    header_text = "No Header"
    wrapper = soup.find('div', class_='container h-100')
    if wrapper:
        header = wrapper.find('div', class_='col')
        header_text = header.text.strip() if header else 'No Header'

    cards = soup.find_all('div', class_='post-list')
    for card in cards:
        title_elem = card.find('div', class_='post-title-block')
        text_elem = card.find('div', class_='post-body')
        
        title = title_elem.text.strip() if title_elem else 'No Title'
        url = title_elem.find('div', class_='post-header').text.strip() if title_elem and title_elem.find('div', class_='post-header') else ''
        text = text_elem.text.strip() if text_elem else 'No Text'

        compare_and_update_data(header_text, title, url, text, 'cards_h3')

# 데이터베이스 초기화
initialize_database()

# .txt 파일을 .html 파일로 변환
directory_path = 'C:\\Users\\whdwns\\Desktop\\tortext'
rename_txt_to_html(directory_path)

# HTML 파일 파싱 및 데이터베이스 저장
parse_and_store_html_h('C:/Users/whdwns/Desktop/tortext/blacksuit.html')
parse_and_store_html_h2('C:/Users/whdwns/Desktop/tortext/bianlian.html')
parse_and_store_html_h3('C:/Users/whdwns/Desktop/tortext/threeamk.html')

# 디버깅: 데이터베이스에서 데이터 확인
def debug_print_table(table):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

# 디버깅 함수 호출
debug_print_table('cards_h1')
debug_print_table('cards_h2')
debug_print_table('cards_h3')
