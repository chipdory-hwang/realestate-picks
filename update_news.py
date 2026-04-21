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
            /* 전체 배경 및 기본 폰트 */
            body {{ 
                font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; 
                line-height: 1.5; color: #333; margin: 0; padding: 10px; 
                background-color: #f0f7f4; -webkit-text-size-adjust: 100%;
            }}
            /* 모바일 꽉 차는 컨테이너 */
            .container {{ 
                width: 100%; max-width: 600px; margin: 0 auto; box-sizing: border-box;
                background: #ffffff; padding: 25px 15px; border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-top: 8px solid #2ecc71; 
            }}
            
            /* 모든 상단 문구 가운데 정렬 */
            .header-section {{ text-align: center; margin-bottom: 25px; }}
            h1 {{ 
                color: #27ae60; font-size: 1.6em; margin: 0; 
                display: inline-block; border-bottom: 3px solid #2ecc71; padding-bottom: 5px; 
            }}
            .sub-title {{ display: block; color: #555; font-size: 0.9em; margin-top: 8px; font-weight: bold; }}
            .date-group {{ margin-top: 15px; }}
            .date {{ color: #7f8c8d; font-size: 0.85em; margin: 0; }}
            .designer {{ font-size: 0.85em; color: #27ae60; font-weight: bold; display: block; margin-top: 3px; }}
            
            /* 뉴스 리스트 레이아웃 */
            ul {{ list-style: none; padding: 0; margin-top: 25px; }}
            li {{ 
                margin-bottom: 12px; padding: 15px; background: #fff; 
                border: 1px solid #e1eedd; border-radius: 10px; 
                display: flex; flex-direction: column; /* 세로 배치로 모바일 최적화 */
                transition: all 0.2s ease; box-sizing: border-box;
            }}
            
            /* PICK 넘버링과 제목 영역 */
            .top-area {{ display: flex; align-items: flex-start; margin-bottom: 8px; }}
            .tag-box {{ 
                background: #2ecc71; color: #fff; padding: 3px 8px; font-size: 0.75em; 
                font-weight: bold; margin-right: 10px; border-radius: 4px; 
                white-space: nowrap; flex-shrink: 0;
            }}
            .news-link {{ 
                text-decoration: none; color: #333; font-weight: 500; font-size: 1.05em; 
                word-break: keep-all; line-height: 1.4;
            }}
            
            /* 매체명 오른쪽 정렬 */
            .bottom-area {{ display: flex; justify-content: flex-end; }}
            .media-name {{ 
                font-size: 0.8em; color: #27ae60; font-weight: bold; 
                background-color: #ebf9f1; padding: 2px 8px; border-radius: 4px; 
                border: 1px solid #d1e7dd; 
            }}
            
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
        html_content += '<li style="text-align: center; color: #27ae60;">현재 새로운 소식을 수집 중입니다.</li>'
    else:
        for i, news in enumerate(news_list, 1):
            html_content += f"""
                <li>
                    <div class="top-area">
                        <div class="tag-box">PICK-{i}</div>
                        <a href='{news['link']}' class="news-link" target='_blank'>{news['title']}</a>
                    </div>
                    <div class="bottom-area">
                        <span class="media-name">{news['media']}</span>
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
