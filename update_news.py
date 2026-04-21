import requests
from bs4 import BeautifulSoup
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_news():
    # 구글 뉴스 RSS 피드 활용 (부동산 관련 통합 검색어)
    # 키워드: 부동산, 아파트, 재건축, 재개발, 토지
    search_query = '부동산 OR 아파트 OR 재건축 OR 재개발 OR 토지'
    url = f"https://news.google.com/rss/search?q={search_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'xml') # RSS는 XML 형식이므로 xml 파서 사용
        news_list = []
        
        items = soup.select('item')
        for item in items[:15]: # 주요 뉴스 15개 수집
            title = item.title.text
            link = item.link.text
            # 불필요한 출처 표시 제거 (예: - 연합뉴스)
            clean_title = title.split(' - ')[0]
            news_list.append({'title': clean_title, 'link': link})
            
        return news_list
    except Exception as e:
        print(f"뉴스 피드 수집 중 상세 에러: {e}")
        return []

def create_html(news_list):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>부동산 이슈 브리핑</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.7; color: #333; max-width: 850px; margin: 0 auto; padding: 25px; background-color: #f8f9fa; }}
            .container {{ background: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-left: 5px solid #e67e22; padding-left: 15px; margin-bottom: 5px; }}
            .date {{ color: #7f8c8d; font-size: 0.95em; margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin-bottom: 12px; padding: 15px; background: #fff; border: 1px solid #e9ecef; border-radius: 8px; transition: transform 0.2s; }}
            li:hover {{ transform: translateX(5px); border-color: #e67e22; }}
            a {{ text-decoration: none; color: #34495e; font-weight: 600; font-size: 1.1em; }}
            a:hover {{ color: #e67e22; }}
            .tag {{ display: inline-block; background: #e67e22; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 8px; vertical-align: middle; }}
            footer {{ margin-top: 40px; font-size: 0.85em; color: #bdc3c7; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 부동산 핵심 이슈 리포트</h1>
            <p class="date">업데이트: {now} (부동산/아파트/재건축/토지)</p>
    """
    
    if not news_list:
        html_content += """
            <p style="padding: 20px; background: #fff5f5; color: #c0392b; border-radius: 8px;">
                현재 뉴스를 불러올 수 없습니다. 시스템 로그를 확인해 주세요.
            </p>
        """
    else:
        html_content += "<ul>"
        for news in news_list:
            html_content += f"<li><span class='tag'>HOT</span><a href='{news['link']}' target='_blank'>{news['title']}</a></li>\n"
        html_content += "</ul>"
        
    html_content += """
            <footer>
                본 리포트는 공개 뉴스 피드를 기반으로 AI가 자동 선별하여 제공합니다.
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ index.html 생성 완료")
    return html_content

def send_email(html_body):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    
    if not email_user or not email_pass:
        print("이메일 설정이 없어 발송을 스킵합니다.")
        return

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_user
    msg['Subject'] = f"🏠 [부동산 리포트] {datetime.date.today()} 주요 뉴스"
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
