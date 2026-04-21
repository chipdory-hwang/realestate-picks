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
                media = "뉴스"
                
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
        <title>Daily 부동산 Picks - Gold Edition</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&family=Noto+Sans+KR:wght@300;400;700&display=swap');
            
            body {{ 
                font-family: 'Noto Sans KR', sans-serif; 
                line-height: 1.8; 
                color: #3d3d3d; 
                max-width: 900px; 
                margin: 0 auto; 
                padding: 50px 20px; 
                background-color: #f9f7f2; /* 연한 베이지 바탕 */
            }}
            .container {{ 
                background: #ffffff; 
                padding: 50px; 
                border-radius: 5px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.08); 
                border-top: 12px solid #D4AF37; /* 골드 포인트 */
            }}
            
            /* 상단 헤더 중앙 정렬 섹션 */
            .header-section {{
                text-align: center;
                margin-bottom: 45px;
            }}
            h1 {{ 
                font-family: 'Noto Serif KR', serif;
                color: #aa8a2e; 
                font-size: 2.8em;
                margin-bottom: 5px;
                display: inline-block;
                border-bottom: 3px solid #D4AF37;
                padding-bottom: 8px;
                letter-spacing: -1px;
            }}
            .sub-title {{
                display: block;
                color: #8a8a8a;
                font-size: 1em;
                margin-top: 15px;
                font-weight: 400;
                letter-spacing: 2px;
            }}
            .date {{ 
                color: #666; 
                font-size: 0.95em; 
                margin-top: 25px;
                margin-bottom: 5px;
            }}
            .designer {{
                font-size: 0.9em;
                color: #D4AF37;
                font-weight: 700;
                margin-bottom: 10px;
                display: block;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            /* 뉴스 리스트 섹션 */
            ul {{ list-style: none; padding: 0; }}
            li {{ 
                margin-bottom: 18px; 
                padding: 22px; 
                background: #fff; 
                border: 1px solid #eeebe0; 
                border-radius: 0px; 
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: space-between; /* 양 끝 정렬 */
            }}
            li:hover {{ 
                background-color: #fffdf5;
                border-color: #D4AF37;
                transform: scale(1.01);
            }}
            
            .left-group {{
                display: flex;
                align-items: center;
                flex: 1;
            }}
            .tag-box {{ 
                background: linear-gradient(135deg, #D4AF37, #F1D38A); 
                color: #fff; 
                padding: 6px 14px; 
                font-size: 0.8em; 
                font-weight: bold;
                margin-right: 20px;
                min-width: 70px;
                text-align: center;
                box-shadow: 2px 2px 8px rgba(212, 175, 55, 0.3);
            }}
            .news-link {{ 
                text-decoration: none; 
                color: #2c2c2c; 
                font-weight: 500; 
                font-size: 1.15em;
                word-break: keep-all;
                flex: 1;
            }}
            .news-link:hover {{ color: #aa8a2e; }}
            
            .media-name {{
                font-size: 0.85em;
                color: #999;
                margin-left: 20px;
                white-space: nowrap;
                border-left: 1px solid #ddd;
                padding-left: 15px;
            }}
            
            footer {{ 
                margin-top: 60px; 
                font-size: 0.85em; 
                color: #b3b3b3; 
                text-align: center;
                border-top: 1px solid #f0f0f0;
                padding-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>Daily「부동산」Picks</h1>
                <span class="sub-title">(부동산/아파트/재건축/재개발/토지)</span>
                <p class="date">📅 {now} UPDATE</p>
                <span class="designer">Designed by chipdory.hwang</span>
            </div>
            
            <div class="content-section">
    """
    
    if not news_list:
        html_content += """
                <p style="padding: 40px; background: #fffdf5; color: #aa8a2e; text-align: center; border: 1px dashed #D4AF37;">
                    현재 새로운 소식을 분석 중입니다. 잠시 후 다시 방문해 주세요.
                </p>
        """
    else:
        html_content += "<ul>"
        for i, news in enumerate(news_list, 1):
            html_content += f"""
                <li>
                    <div class="left-group">
                        <div class="tag-box">PICK-{i}</div>
                        <a href='{news['link']}' class="news-link" target='_blank'>{news['title']}</a>
                    </div>
                    <span class="media-name">{news['media']}</span>
                </li>\n"""
        html_content += "</ul>"
        
    html_content += """
            </div>
            <footer>
                PREMIUM REAL ESTATE NEWS CURATION<br>
                본 리포트는 매일 오전 5시 18분에 업데이트됩니다.
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
    msg['Subject'] = f"✨ [Daily 부동산 Picks] {datetime.date.today()} Gold 리포트"
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
    except Exception:
        pass

if __name__ == "__main__":
    news_data = get_news()
    full_html = create_html(news_data)
    if news_data:
        send_email(full_html)
