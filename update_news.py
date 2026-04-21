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
            
            if ' - ' in full_title:
                parts = full_title.rsplit(' - ', 1)
                title = parts[0]
                media = parts[1]
            else:
                title = full_title
                media = "Media"
                
            news_list.append({'title': title, 'link': link, 'media': media})
            
        return news_list
    except Exception as e:
        print(f"뉴스 수집 중 에러: {e}")
        return []

def create_html(news_list):
    now = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily 부동산 Picks - Prestige Gold</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Noto+Serif+KR:wght@700&family=Noto+Sans+KR:wght@300;400;700&display=swap');
            
            body {{ 
                font-family: 'Noto Sans KR', sans-serif; 
                line-height: 1.8; 
                color: #1a1a1a; 
                max-width: 900px; 
                margin: 0 auto; 
                padding: 40px 20px; 
                background-color: #111111; /* 다크 배경으로 금색 극대화 */
            }}
            .container {{ 
                background: #ffffff; 
                padding: 40px; 
                border-radius: 0px; 
                box-shadow: 0 0 50px rgba(184, 134, 11, 0.2); 
                border: 1px solid #d4af37;
            }}
            
            /* 헤더 섹션 중앙 정렬 및 간격 축소 */
            .header-section {{
                text-align: center;
                margin-bottom: 40px;
            }}
            h1 {{ 
                font-family: 'Cinzel', serif; /* 럭셔리 영문 서체 혼용 가능 */
                color: #996515; 
                font-size: 3.2em;
                margin: 0;
                padding: 0;
                line-height: 1.1;
                display: inline-block;
                background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                border-bottom: 2px solid #d4af37;
            }}
            .sub-title {{
                display: block;
                color: #b8860b;
                font-size: 1.1em;
                margin-top: 5px; /* 제목과의 간격 축소 */
                font-weight: 700;
                letter-spacing: 1px;
            }}
            .date-group {{
                margin-top: 20px;
            }}
            .date {{ 
                color: #666; 
                font-size: 0.9em; 
                margin: 0;
            }}
            .designer {{
                font-size: 0.85em;
                color: #aa771c;
                font-weight: 700;
                display: block;
                margin-top: 5px;
                letter-spacing: 2px;
            }}
            
            /* 리스트 섹션 */
            ul {{ list-style: none; padding: 0; margin-top: 30px; }}
            li {{ 
                margin-bottom: 12px; 
                padding: 15px 20px; 
                background: #fff; 
                border-bottom: 1px solid #f0e6cc; 
                display: flex;
                align-items: center;
                justify-content: space-between;
                transition: all 0.3s ease;
            }}
            li:hover {{ 
                background-color: #fffaf0;
                border-left: 5px solid #d4af37;
            }}
            
            .left-group {{
                display: flex;
                align-items: center;
                flex: 1;
            }}
            .tag-box {{ 
                background: #111; 
                color: #d4af37; 
                padding: 4px 10px; 
                font-size: 0.75em; 
                font-weight: bold;
                margin-right: 15px;
                border: 1px solid #d4af37;
                min-width: 60px;
                text-align: center;
            }}
            .news-link {{ 
                text-decoration: none; 
                color: #222; 
                font-weight: 500; 
                font-size: 1.05em;
                word-break: keep-all;
            }}
            
            /* 매체 출처 가독성 강화 */
            .media-name {{
                font-size: 0.9em;
                color: #111;
                font-weight: 700;
                margin-left: 20px;
                white-space: nowrap;
                background-color: #fcf6ba;
                padding: 2px 8px;
                border-radius: 4px;
                border: 1px solid #d4af37;
            }}
            
            footer {{ 
                margin-top: 50px; 
                font-size: 0.8em; 
                color: #999; 
                text-align: center;
                letter-spacing: 1px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>Daily 부동산 Picks</h1>
                <span class="sub-title">(부동산/아파트/재건축/재개발/토지)</span>
                <div class="date-group">
                    <p class="date">📅 {now} UPDATE</p>
                    <span class="designer">Designed by chipdory.hwang</span>
                </div>
            </div>
            
            <ul>
    """
    
    if not news_list:
        html_content += """
                <li style="justify-content: center; color: #b8860b;">데이터를 불러오는 중입니다.</li>
        """
    else:
        for i, news in enumerate(news_list, 1):
            html_content += f"""
                <li>
                    <div class="left-group">
                        <div class="tag-box">PICK-{i}</div>
                        <a href='{news['link']}' class="news-link" target='_blank'>{news['title']}</a>
                    </div>
                    <span class="media-name">{news['media']}</span>
                </li>\n"""
        
    html_content += """
            </ul>
            <footer>
                PREMIUM CURATION SERVICE BY CHIPDORY HWANG
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
    if not email_user or not email_pass: return

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_user
    msg['Subject'] = f"🏆 [Prestige Gold] {datetime.date.today()} 부동산 리포트"
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
    except: pass

if __name__ == "__main__":
    news_data = get_news()
    full_html = create_html(news_data)
    if news_data:
        send_email(full_html)
