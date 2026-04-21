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
        <title>Daily 부동산 Picks</title>
        <style>
            body {{ 
                font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; 
                line-height: 1.6; color: #333; max-width: 850px; margin: 0 auto; padding: 40px 20px; background-color: #f0f7f4; 
            }}
            .container {{ background: #ffffff; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-top: 8px solid #2ecc71; }}
            .header-section {{ text-align: center; margin-bottom: 35px; }}
            h1 {{ color: #27ae60; font-size: 2.5em; margin: 0; padding: 0; display: inline-block; border-bottom: 3px solid #2ecc71; padding-bottom: 5px; }}
            .sub-title {{ display: block; color: #555; font-size: 0.95em; margin-top: 8px; font-weight: bold; }}
            .date-group {{ margin-top: 15px; }}
            .date {{ color: #7f8c8d; font-size: 0.9em; margin: 0; }}
            .designer {{ font-size: 0.85em; color: #27ae60; font-weight: bold; display: block; margin-top: 3px; }}
            ul {{ list-style: none; padding: 0; margin-top: 25px; }}
            li {{ margin-bottom: 12px; padding: 15px 20px; background: #fff; border: 1px solid #e1eedd; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; transition: all 0.2s ease; }}
            li:hover {{ transform: translateX(5px); border-color: #2ecc71; background-color: #f9fffb; }}
            .left-group {{ display: flex; align-items: center; flex: 1; }}
            .tag-box {{ background: #2ecc71; color: #fff; padding: 4px 10px; font-size: 0.75em; font-weight: bold; margin-right: 15px; border-radius: 5px; min-width: 55px; text-align: center; }}
            .news-link {{ text-decoration: none; color: #333; font-weight: 500; font-size: 1.05em; word-break: keep-all; }}
            .media-name {{ font-size: 0.85em; color: #27ae60; font-weight: bold; margin-left: 20px; white-space: nowrap; background-color: #ebf9f1; padding: 3px 10px; border-radius: 5px; border: 1px solid #d1e7dd; }}
            footer {{ margin-top: 50px; font-size: 0.8em; color: #999; text-align: center; }}
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
        html_content += '<li style="justify-content: center; color: #27ae60;">현재 업데이트된 소식이 없습니다. 잠시 후 확인해주세요.</li>'
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
            <footer>© 2026 Daily 부동산 Picks - All Rights Reserved.</footer>
        </div>
    </body>
    </html>
    """
    
    # [핵심] 어떤 상황에서도 파일을 생성하도록 보장
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ index.html 파일 생성 완료")
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
    # 데이터 유무와 상관없이 파일을 만듦
    create_html(news_data)
    if news_data:
        send_email(create_html(news_data))
