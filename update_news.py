import requests
from bs4 import BeautifulSoup
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_news():
    # 여러 네이버 뉴스 섹션 시도 (크롤링 안정성 보강)
    url = "https://land.naver.com/news/main.naver"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        news_list = []
        
        # 선택자 보강: 뉴스 리스트를 찾는 여러 시도
        items = soup.select('.news_list li') or soup.select('.section_headline li')
        
        for item in items[:10]:
            link_tag = item.select_one('dt:not(.photo) a') or item.select_one('a')
            if link_tag:
                title = link_tag.text.strip()
                link = link_tag['href']
                if not link.startswith('http'):
                    link = "https://land.naver.com" + link
                news_list.append({'title': title, 'link': link})
        return news_list
    except Exception as e:
        print(f"뉴스 수집 중 상세 에러: {e}")
        return []

def create_html(news_list):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 기본 헤더
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
            .error-msg {{ color: #d35400; background: #fdf2e9; padding: 10px; border-radius: 5px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin-bottom: 15px; padding: 10px; border: 1px solid #eee; border-radius: 5px; }}
            a {{ text-decoration: none; color: #2c3e50; font-weight: bold; }}
            a:hover {{ color: #e67e22; }}
        </style>
    </head>
    <body>
        <h1>🏠 오늘의 부동산 주요 뉴스</h1>
        <p class="date">최근 시도 시간: {now}</p>
    """
    
    if not news_list:
        html_content += """
        <div class="error-msg">
            <p>📢 현재 뉴스 데이터를 가져오는 데 일시적인 문제가 발생했습니다.</p>
            <p>GitHub Actions 로그를 확인하거나 잠시 후 다시 시도해 주세요.</p>
        </div>
        """
    else:
        html_content += "<ul>"
        for news in news_list:
            html_content += f"<li><a href='{news['link']}' target='_blank'>{news['title']}</a></li>\n"
        html_content += "</ul>"
        
    html_content += """
        <footer style="margin-top: 30px; font-size: 0.8em; color: #999;">
            본 페이지는 GitHub Actions를 통해 자동 생성됩니다.
        </footer>
    </body>
    </html>
    """
    
    # 무조건 index.html 파일을 생성함
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ index.html 파일이 성공적으로 기록되었습니다.")
    return html_content

def send_email(html_body):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    
    if not email_user or not email_pass:
        print("메일 설정이 없어 발송을 스킵합니다.")
        return

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_user
    msg['Subject'] = f"🏠 [부동산 뉴스] {datetime.date.today()} 리포트"
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
    # 뉴스가 있든 없든 create_html을 실행하여 파일을 만듦
    full_html = create_html(news_data)
    if news_data:
        send_email(full_html)
