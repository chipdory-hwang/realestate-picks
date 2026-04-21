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
        for item in items[:15]:
            full_title = item.title.text
            link = item.link.text
            
            # 언론사 분리 (제목 - 언론사 형식)
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
        print(f"뉴스 수집 중 상세 에러: {e}")
        return []

def create_html(news_list):
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
                max-width: 850px; 
                margin: 0 auto; 
                padding: 40px 20px; 
                background-color: #f2f9f4; 
            }}
            .container {{ 
                background: #ffffff; 
                padding: 45px; 
                border-radius: 25px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.05); 
                border-top: 10px solid #48c774;
            }}
            .header-group {{ margin-bottom: 35px; }}
            h1 {{ 
                color: #234d32; 
                font-size: 2.5em;
                margin-bottom: 5px;
                display: inline-block;
                border-bottom: 4px solid #48c774; /* 제목 밑줄 */
                padding-bottom: 5px;
            }}
            .sub-title {{
                display: block;
                color: #555;
                font-size: 0.95em;
                margin-top: 10px;
                font-weight: 400;
            }}
            .date {{ 
                color: #7f8c8d; 
                font-size: 0.9em; 
                margin-top: 20px;
                margin-bottom: 5px;
            }}
            .designer {{
                font-size: 0.85em;
                color: #48c774;
                font-weight: bold;
                margin-bottom: 30px;
                display: block;
            }}
            ul {{ list-style: none; padding: 0; }}
            li {{ 
                margin-bottom: 15px; 
                padding: 20px; 
                background: #fff; 
                border: 1px solid #e1eedd; 
                border-radius: 15px; 
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
            }}
            li:hover {{ 
                transform: translateX(8px);
                border-color: #48c774;
                background-color: #f9fffb;
            }}
            .tag-box {{ 
                background: #48c774; 
                color: #fff; 
                padding: 5px 12px; 
                border-radius: 8px; 
                font-size: 0.75em; 
                font-weight: bold;
                margin-right: 15px;
                min-width: 110px;
                text-align: center;
                box-shadow: 2px 2px 5px rgba(72, 199, 116, 0.2);
            }}
            a {{ 
                text-decoration: none; 
                color: #2d3436; 
                font-weight: 500; 
                font-size: 1.1em;
                word-break: keep-all;
            }}
            a:hover {{ color: #1a7a3a; }}
            footer {{ 
                margin-top: 60px; 
                font-size: 0.8em; 
                color: #95a5a6; 
                text-align: center;
                border-top: 1px solid #eee;
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-group">
                <h1>Daily「부동산」Picks</h1>
                <span class="sub-title">(부동산/아파트/재건축/재개발/토지)</span>
            </div>
            
            <p class="date">📅 {now} 업데이트</p>
            <span class="designer">Designed by chipdory.hwang</span>
    """
    
    if not news_list:
        html_content += """
            <p style="padding: 30px; background: #f0fdf4; color: #234d32; border-radius: 15px; text-align: center;">
                현재 수집된 소식이 없습니다. 잠시 후 다시 확인해 주세요.
            </p>
        """
    else:
        html_content += "<ul>"
        for i, news in enumerate(news_list, 1):
            html_content += f"""
            <li>
                <div class="tag-box">PICK-{i} {news['media']}</div>
                <a href='{news['link']}' target='_blank'>{news['title']}</a>
            </li>\n"""
        html_content += "</ul>"
        
    html_content += """
            <footer>
                본 서비스는 매일 오전 5시 18분에 자동으로 뉴스 큐레이션을 수행합니다.<br>
                © 2026 Daily 부동산 Picks All Rights Reserved.
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
