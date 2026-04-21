import requests
from bs4 import BeautifulSoup
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_news():
    # 구글 뉴스 RSS 피드 (부동산 핵심 키워드 검색)
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
        for item in items[:15]:
            title = item.title.text
            link = item.link.text
            clean_title = title.split(' - ')[0]
            news_list.append({'title': clean_title, 'link': link})
            
        return news_list
    except Exception as e:
        print(f"뉴스 수집 중 상세 에러: {e}")
        return []

def create_html(news_list):
    # 한국 시간 기준 시간 표시 (GitHub Actions 서버 시간 고려)
    now = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily 부동산 Picks</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
            
            body {{ 
                font-family: 'Noto Sans KR', sans-serif; 
                line-height: 1.8; 
                color: #2d3436; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 40px 20px; 
                background-color: #f0f7f4; 
            }}
            .container {{ 
                background: #ffffff; 
                padding: 40px; 
                border-radius: 20px; 
                box-shadow: 0 15px 35px rgba(46, 204, 113, 0.1); 
                border-top: 8px solid #2ecc71;
            }}
            h1 {{ 
                color: #27ae60; 
                font-size: 2.2em;
                margin-bottom: 10px;
                letter-spacing: -1px;
                display: flex;
                align-items: center;
            }}
            h1 span {{ color: #2d3436; margin: 0 5px; }}
            .date {{ 
                color: #7f8c8d; 
                font-size: 0.95em; 
                margin-bottom: 30px; 
                padding-bottom: 15px;
                border-bottom: 1px dashed #bddfc3;
            }}
            ul {{ list-style: none; padding: 0; }}
            li {{ 
                margin-bottom: 15px; 
                padding: 18px; 
                background: #fff; 
                border: 1px solid #e1eedd; 
                border-radius: 12px; 
                transition: all 0.3s ease;
                display: flex;
                align-items: flex-start;
            }}
            li:hover {{ 
                transform: translateY(-3px); 
                border-color: #2ecc71; 
                box-shadow: 0 5px 15px rgba(46, 204, 113, 0.15);
            }}
            .tag {{ 
                background: #2ecc71; 
                color: #fff; 
                padding: 3px 10px; 
                border-radius: 6px; 
                font-size: 0.75em; 
                font-weight: bold;
                margin-right: 12px;
                margin-top: 4px;
                white-space: nowrap;
            }}
            a {{ 
                text-decoration: none; 
                color: #2d3436; 
                font-weight: 500; 
                font-size: 1.05em;
                word-break: keep-all;
            }}
            a:hover {{ color: #27ae60; }}
            footer {{ 
                margin-top: 50px; 
                font-size: 0.85em; 
                color: #95a5a6; 
                text-align: center;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Daily<span>「부동산」</span>Picks</h1>
            <p class="date">📅 <b>{now}</b> 기준 최신 브리핑</p>
    """
    
    if not news_list:
        html_content += """
            <p style="padding: 20px; background: #ebf9f1; color: #27ae60; border-radius: 12px; text-align: center;">
                현재 분석 중인 이슈가 없습니다. 잠시 후 다시 확인해주세요.
            </p>
        """
    else:
        html_content += "<ul>"
        for news in news_list:
            html_content += f"<li><span class='tag'>PICK</span><a href='{news['link']}' target='_blank'>{news['title']}</a></li>\n"
        html_content += "</ul>"
        
    html_content += """
            <footer>
                본 리포트는 매일 오전 5시 18분에 자동 업데이트됩니다.<br>
                © 2026 부동산 뉴스 큐레이션 시스템
            </footer>
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
    
    if not email_user or not email_pass:
        return

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_user
    msg['Subject'] = f"🌿 [Daily 부동산 Picks] {datetime.date.today()} 리포트"
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
        print("메일 발송 성공!")
    except Exception as e:
        print(f"메일 실패: {e}")

if __name__ == "__main__":
    news_data = get_news()
    full_html = create_html(news_data)
    if news_data:
        send_email(full_html)
