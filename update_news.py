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
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Daily 부동산 Picks</title>
        <style>
            body {{ 
                font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; 
                line-height: 1.5; color: #333; max-width: 800px; margin: 0 auto; 
                padding: 20px 15px; background-color: #f0f7f4; 
                -webkit-text-size-adjust: none;
            }}
            .container {{ 
                background: #ffffff; padding: 25px 20px; border-radius: 12px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 6px solid #2ecc71; 
            }}
            .header-section {{ text-align: center; margin-bottom: 25px; }}
            h1 {{ 
                color: #27ae60; font-size: 1.8em; margin: 0; padding: 0; 
                display: inline-block; border-bottom: 2px solid #2ecc71; padding-bottom: 3px; 
            }}
            .sub-title {{ display: block; color: #555; font-size: 0.85em; margin-top: 8px; font-weight: bold; }}
            .date-group {{ margin-top: 12px; }}
            .date {{ color: #888; font-size: 0.8em; margin: 0; }}
            .designer {{ font-size: 0.8em; color: #27ae60; font-weight: bold; display: block; margin-top: 2px; }}
            
            ul {{ list-style: none; padding: 0; margin-top: 20px; }}
            li {{ 
                margin-bottom: 10px; padding: 12px; background: #fff; border: 1px solid #e1eedd; 
                border-radius: 8px; display: flex; flex-direction: column; transition: background 0.2s;
            }}
            li:active {{ background-color: #f0fdf4; }} /* 모바일 터치 피드백 */
            
            .left-group {{ display: flex; align-items: flex-start; margin-bottom: 6px; }}
            .tag-box {{ 
                background: #2ecc71; color: #fff; padding: 2px 8px; font-size: 0.7em; 
                font-weight: bold; margin-right: 10px; border-radius: 4px; 
                min-width: 45px; text-align: center; margin-top: 2px;
            }}
            .news-link {{ 
                text-decoration: none; color: #333; font-weight: 500; font-size: 1.05em; 
                word-break: keep-all; flex: 1; line-height: 1.4;
            }}
            
            .media-info {{
                display: flex; justify-content: flex-end; align-items: center;
            }}
            .media-name {{ 
                font-size: 0.75em; color: #27ae60; font-weight: bold; 
                background-color: #ebf9f1; padding: 2px 8px; border-radius: 4px; 
                border: 1px solid #d1e7dd; 
            }}
            
            footer {{ margin-top: 30px; font-size: 0.75em; color: #aaa; text-align: center; line-height: 1.4; }}
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
        html_content += '<li style="text-align: center; color: #27ae60;">현재 업데이트된 소식이 없습니다.</li>'
    else:
        for i, news in enumerate(news_list, 1):
            html_content += f"""
                <li>
                    <div class="left-group">
                        <div class="tag-box">P-{i}</div>
                        <a href='{news['link']}' class="news-link" target='_blank'>{news['title']}</a>
                    </div>
                    <div class="media-info">
                        <span class="media-name">{news['media']}</span>
                    </div>
                </li>\n"""
        
    html_content += """
