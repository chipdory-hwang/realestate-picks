import requests
from bs4 import BeautifulSoup
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_news():
    # 네이버 부동산 뉴스 (주요 뉴스)
    url = "https://land.naver.com/news/main.naver"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        news_list = []
        
        # 주요 뉴스 리스트 추출
        items = soup.select('.news_list li')[:10] # 상위 10개
        for item in items:
            title = item.select_one('dt:not(.photo) a').text.strip()
            link = "https://land.naver.com" + item.select_one('dt:not(.photo) a')['href']
            news_list.append({'title': title, 'link': link})
        return news_list
    except Exception as e:
        print(f"뉴스 수집 중 에러 발생: {e}")
        return []

def create_html(news_list):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>오늘의 부동산 뉴스</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #e67e22; border-bottom: 2px solid #e67e22; padding-bottom: 10px; }}
            .date {{ color: #666; font-size: 0.9em; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin-bottom: 15px; padding: 10px; border: 1px solid #eee; border-radius: 5px; }}
            a {{ text-decoration: none; color: #2c3e50; font-weight: bold; }}
            a:hover {{ color: #e67e22; }}
        </style>
    </head>
    <body>
        <h1>🏠 오늘의 부동산 주요 뉴스</h1>
        <p class="date">업데이트 시간: {now}</p>
        <ul>
    """
    
    for news in news_list:
        html_content += f"<li><a href='{news['link']}' target='_blank'>{news['title']}</a></li>\n"
        
    html_content += """
        </ul>
        <footer style="margin-top: 30px; font-size: 0.8em; color: #999;">
            본 리포트는 네이버 부동산 뉴스를 기반으로 자동 생성되었습니다.
        </footer>
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
        print("이메일 설정(Secrets)이 되어있지 않아 메일 발송을 건너뜁니다.")
        return

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_user # 나에게 보내기
    msg['Subject'] = f"🏠 [부동산 뉴스] {datetime.date.today()} 리포트"
    
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        with smtplib.SMTP_HOST('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
        print("메일 발송 성공!")
    except Exception as e:
        print(f"메일 발송 실패: {e}")

if __name__ == "__main__":
    news_data = get_news()
    if news_data:
        html_text = create_html(news_data)
        send_email(html_text)
    else:
        print("수집된 뉴스가 없어 작업을 중단합니다.")
