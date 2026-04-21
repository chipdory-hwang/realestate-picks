import requests
from bs4 import BeautifulSoup
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_news():
    search_query = '부동산 OR 아파트 OR 재건축 OR 재개발 OR 토지'
    url = f"https://news.google.com/rss/search?q={search_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'xml')
        news_list = []
        
        items = soup.select('item')
        for item in items[:12]: # 모바일 화면을 위해 12개로 소폭 조정
            full_title = item.title.text
            link = item.link.text
            
            if ' - ' in full_title:
                parts = full_title.rsplit(' - ', 1)
                title = parts[0]
                media = parts[1]
            else:
                title = full_title
                media = "뉴스"
                
            news_list.append({'title': title, 'link': link, 'media': media})
        return news_list
    except Exception as e:
        print(f"뉴스 수집 중 에러: {e}")
        return []

def create_html(news_list):
    now = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%m/%dd %H:%M')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                line-height: 1.4; color: #333; margin: 0; padding: 10px; background-color: #f4f9f6; 
                -webkit-text-size-adjust: 100%;
            }}
            .container {{ 
                background: #ffffff; padding: 15px 12px; border-radius: 10px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-top: 5px solid #2ecc71; 
            }}
            .header-section {{ text-align: center; margin-bottom: 15px; }}
            h1 {{ 
                color: #27ae60; font-size: 1.4em; margin: 0; letter-spacing: -1px;
                display: inline-block; border-bottom: 2px solid #2ecc71;
            }}
            .sub-title {{ display: block; color: #666; font-size: 0.75em; margin-top: 4px; font-weight: bold; }}
            .date-info {{ color: #999; font-size: 0.7em; margin-top: 5px; }}
            
            ul {{ list-style: none; padding: 0; margin-top: 10px; }}
            li {{ 
                margin-bottom: 8px; padding: 10px; background: #fff; border: 1px solid #eef5f0; 
                border-radius: 6px; display: block; transition: background 0.1s;
            }}
            li:active {{ background-color: #e8f5e9; }}
            
            .title-area {{ display: flex; align-items: flex-start; margin-bottom: 4px; }}
            .tag {{ 
                background: #2ecc71; color: #fff; padding: 1px 5px; font-size: 0.65em; 
                font-weight: bold; margin-right: 8px; border-radius: 3px; 
                min-width: 32px; text-align: center; margin-top: 2px;
            }}
            .news-link {{ 
                text-decoration: none; color: #222; font-weight: 500; font-size: 0.95em; 
                word-break: keep-all; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
            }}
            
            .meta-area {{ display: flex; justify-content: flex-end; align-items: center; }}
            .media-name {{ 
                font-size: 0.7em; color: #27ae60; font-weight: bold; 
                background-color: #f0faf4; padding: 1px 6px; border-radius: 3px; 
                border: 1px solid #d1e7dd; 
            }}
            
            footer {{ margin-top: 20px; font-size: 0.65em; color: #bbb; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>Daily 부동산 Picks</h1>
                <span class="sub-title">부동산/아파트/재개발 핵심 요약</span>
                <div class="date-info">📅 {now} UPDATE | By chipdory</div>
            </div>
            <ul>
    """
    
    if not news_list:
        html_content += '<li style="text-align: center; font-size: 0.9em; color: #27ae60;">소식이 없습니다.</li>'
    else:
        for i, news in enumerate(news_list, 1):
            html_content += f"""
                <li>
                    <div class="title-area">
                        <span class="tag">#{i}</span>
                        <a href='{news['link']}' class="news-link" target='_blank'>{news['title']}</a>
                    </div>
                    <div class="meta-area">
                        <span class="media-name">{news['media']}</span>
                    </div>
                </li>\n"""
        
    html_content += """
            </ul>
            <footer>© 2026 Daily 부동산 Picks</footer>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    return html_content

def send_email(html_body):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    if not email_user or not email_pass: return

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_user
    msg['Subject'] = f"🌿 [Picks] {datetime.date.today()} 부동산 리포트"
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
    except: pass

if __name__ == "__main__":
    news_data = get_news()
    create_html(news_data)
    if news_data:
        send_email(create_html(news_data))
