import feedparser
import datetime
import ssl
import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 인코딩 및 SSL 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
ssl._create_default_https_context = ssl._create_unverified_context

def get_seoul_time():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    kor_timezone = datetime.timezone(datetime.timedelta(hours=9))
    return now_utc.astimezone(kor_timezone).strftime("%Y.%m.%d %H:%M")

def fetch_real_estate_news():
    query = "부동산 OR 아파트 OR 재건축 OR 재개발 OR 신도시 OR 토지"
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    all_news = []
    
    for entry in feed.entries[:10]:
        title, media = entry.title, "부동산 소식"
        if " - " in entry.title:
            title, media = entry.title.rsplit(" - ", 1)
        all_news.append({
            "media": media.strip(),
            "title": title.strip(),
            "link": entry.link
        })
    return all_news

def create_html(news_data):
    today = get_seoul_time()
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily 부동산 Picks</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{ background: #f4f7f6; font-family: 'Pretendard', sans-serif; color: #333; }}
        .header {{ text-align: center; padding: 45px 20px; background: #fff; border-bottom: 1px solid #eee; margin-bottom: 30px; }}
        .header h2 {{ font-weight: 900; color: #111; margin-bottom: 10px; text-decoration: underline; text-underline-offset: 8px; text-decoration-thickness: 3px; text-decoration-color: #e67e22; }}
        .category {{ font-weight: 700; font-size: 0.95rem; color: #444; margin-bottom: 15px; }}
        .update-info {{ font-size: 0.85rem; color: #777; margin-bottom: 3px; }}
        .designer {{ font-size: 0.85rem; color: #e67e22; font-weight: 600; }}
        .news-grid {{ max-width: 600px; margin: 0 auto; padding: 0 15px 60px; }}
        .news-card {{ background: #fff; border-radius: 14px; margin-bottom: 18px; box-shadow: 0 3px 12px rgba(0,0,0,0.06); overflow: hidden; border: 1px solid #eee; text-decoration: none; display: block; color: inherit; }}
        .card-table {{ width: 100%; border-collapse: collapse; }}
        .row-top {{ background: #fcfcfc; border-bottom: 1px solid #f0f0f0; }}
        .cell-num {{ width: 55px; text-align: center; font-weight: 900; color: #e67e22; font-size: 1.15rem; padding: 12px 0; }}
        .cell-media {{ padding: 12px 10px; font-weight: 700; color: #555; font-size: 0.9rem; }}
        .row-content {{ padding: 20px; }}
        .card-title {{ font-size: 1.15rem; font-weight: 800; color: #111; line-height: 1.5; margin-bottom: 15px; }}
        .link-btn {{ color: #e67e22; font-weight: 700; font-size: 0.95rem; border-top: 1px solid #f1f1f1; padding-top: 12px; text-align: right; }}
    </style>
</head>
<body>
    <header class="header">
        <h2>Daily「부동산」Picks</h2>
        <div class="category">부동산 / 아파트 / 재건축·재개발 / 신도시 / 토지</div>
        <p class="update-info">최종 업데이트: {today}</p>
        <p class="designer">Designed by chipdory.hwang</p>
    </header>
    <div class="news-grid">
    """
    for i, news in enumerate(news_data):
        html_content += f"""
        <a href="{news['link']}" target="_blank" class="news-card">
            <table class="card-table">
                <tr class="row-top">
                    <td class="cell-num">{i+1:02d}</td>
                    <td class="cell-media">{news['media']}</td>
                </tr>
            </table>
            <div class="row-content">
                <div class="card-title">{news['title']}</div>
                <div class="link-btn">원본확인 🖱️</div>
            </div>
        </a>
        """
    html_content += "</div></body></html>"
    return html_content

def send_email(content):
    sender = os.environ.get('EMAIL_USER')
    password = os.environ.get('EMAIL_PASS')
    if not sender or not password:
        print("이메일 설정이 누락되었습니다.")
        return
        
    msg = MIMEMultipart()
    msg['Subject'] = f"[Daily 부동산 Picks] {get_seoul_time()} 리포트"
    msg['From'] = f"부동산 브리핑 봇 <{sender}>"
    msg['To'] = "chipdory@gmail.com"
    msg.attach(MIMEText(content, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
            print("메일 발송 성공!")
    except Exception as e:
        print(f"메일 발송 실패: {e}")

if __name__ == "__main__":
    news = fetch_real_estate_news()
    if news:
        html = create_html(news)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        send_email(html)
