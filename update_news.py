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
        print(f"뉴스 수집 에러: {e}")
        return []

def create_html(news_list):
    now = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
        <style>
            body {{ 
                font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; 
                line-height: 1.5; color: #333; margin: 0; padding: 10px; 
                background-color: #f0f7f4; -webkit-text-size-adjust: 100%;
            }}
            .container {{ 
                width: 100%; max-width: 600px; margin: 0 auto; box-sizing: border-box;
                background: #ffffff; padding: 25px 15px; border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-top: 8px solid #2ecc71; 
            }}
            
            .header-section {{ text-align: center; margin-bottom: 25px; }}
            h1 {{ 
                color: #27ae60; font-size: 1.6em; margin: 0; 
                display: inline-block; border-bottom: 3px solid #2ecc71; padding-bottom: 5px; 
            }}
            .sub-title {{ display: block; color: #555; font-size: 0.9em; margin-top: 8px; font-weight: bold; }}
            .date-group {{ margin-top: 15px; }}
            .date {{ color: #7f8c8d; font-size: 0.85em; margin: 0; }}
            .designer {{ font-size: 0.85em; color: #27ae60; font-weight: bold; display: block; margin-top: 3px; }}
            
            ul {{ list-style: none; padding: 0; margin-top: 25px; }}
            li {{ 
                margin-bottom: 15px; padding: 18px; background: #fff; 
                border: 1px solid #e1eedd; border-radius: 10px; 
                box-sizing: border-box; position: relative;
            }}
            
            /* [상단 배치] PICK-넘버링 | 매체출처 (가운데 정렬) */
            .top-meta {{ 
                display: flex; justify-content: center; align-items: center; 
                gap: 8px; margin-bottom: 12px; 
            }}
            .tag-box {{ 
                background: #2ecc71; color: #fff; padding: 2px 8px; font-size: 0.75em; 
                font-weight: bold; border-radius: 4px; 
            }}
            .media-name {{ 
                font-size: 0.8em; color: #27ae60; font-weight: bold; 
                background-color: #ebf9f1; padding: 2px 8px; border-radius: 4px; 
                border: 1px solid #d1e7dd; 
            }}
            
            /* [중간 배치] 제목 */
            .title-area {{ text-align: center; margin-bottom: 15px; }}
            .news-title {{ 
                text-decoration: none; color: #111; font-weight: bold; font-size: 1.1em; 
                word-break: keep-all; line-height: 1.4; display: block;
            }}
            
            /* [하단 배치] 원본확인 버튼 | 생쥐 캐릭터 */
            .bottom-area {{ 
                display: flex; justify-content: space-between; align-items: flex-end; 
                border-top: 1px dashed #e1eedd; padding-top: 10px;
            }}
            .origin-btn {{
                text-decoration: none; color: #fff; background-color: #27ae60; 
                padding: 5px 12px; font-size: 0.8em; border-radius: 20px; font-weight: bold;
            }}
            .mouse-char {{ font-size: 1.5em; }} /* 이모지로 생쥐 표현 (또는 이미지 태그 사용 가능) */
            
            footer {{ margin-top: 40px; font-size: 0.8em; color: #999; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>Daily「부동산」Picks</h1>
                <span class="sub-title">(부동산/아파트/재건축/재개발/토지)</span>
                <div class="date-group">
                    <p class="date">📅 {now} UPDATE</p>
                    <span class="designer">Designed by chipdory.hwang</span>
                </div>
            </div>
            
            <ul>
    """
    
    if not news_list:
        html_content += '<li style="text-align: center; color: #27ae60;">소식을 수집하고 있습니다.</li>'
    else:
        for i, news in enumerate(news_list, 1):
            html_content += f"""
                <li>
                    <div class="top-meta">
                        <span class="tag-box">PICK-{i}</span>
                        <span class="media-name">{news['media']}</span>
                    </div>
                    <div class="title-area">
                        <span class="news-title">{news['title']}</span>
                    </div>
                    <div class="bottom-area">
                        <a href="{news['link']}" class="origin-btn" target="_blank">원본 확인하기</a>
                        <span class="mouse-char">🐭</span>
                    </div>
                </li>\n"""
        
    html_content += """
            </ul>
            <footer>© 2026 Daily 부동산 Picks - All Rights Reserved.</footer>
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
    msg['Subject'] = f"🌿 [Daily 부동산 Picks] {datetime.date.today()} 리포트"
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
