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
        <title>Daily 부동산 Picks</title>
        <style>
            /* 초기 버전의 깔끔한 글꼴 설정 */
            body {{ 
                font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; 
                line-height: 1.6; 
                color: #333; 
                max-width: 850px; 
                margin: 0 auto; 
                padding: 40px 20px; 
                background-color: #f0f7f4; 
            }}
            .container {{ 
                background: #ffffff; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
                border-top: 8px solid #2ecc71;
            }}
            
            /* 헤더 섹션 중앙 정렬 및 간격 조정 */
            .header-section {{
                text-align: center;
                margin-bottom: 35px;
            }}
            h1 {{ 
                color: #27ae60; 
                font-size: 2.5em;
                margin: 0;
                padding: 0;
                display: inline-block;
                border-bottom: 3px solid #2ecc71;
                padding-bottom: 5px;
            }}
            .sub-title {{
                display: block;
                color: #555;
                font-size: 0.95em;
                margin-top: 8px; /* 간격 축소 반영 */
                font-weight: bold;
            }}
            .date-group {{
                margin-top: 15px;
            }}
            .date {{ 
                color: #7f8c8d; 
                font-size: 0.9em; 
                margin: 0;
            }}
            .designer {{
                font-size: 0.85em;
                color: #27ae60;
                font-weight: bold;
                display: block;
                margin-top: 3px;
            }}
            
            /* 뉴스 리스트 섹션 */
            ul {{ list-style: none; padding: 0; margin-top: 25px; }}
            li {{ 
                margin-bottom: 12px; 
                padding: 15px 20px; 
                background: #fff; 
                border: 1px solid #e1eedd; 
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                transition: all 0.2s ease;
            }}
            li:hover {{ 
                transform: translateX(5px);
                border-color: #2ecc71;
                background-color: #f9fffb;
            }}
            
            .left-group {{
                display: flex;
                align-items: center;
                flex: 1;
            }}
            .tag-box {{ 
                background: #2ecc71; 
                color: #fff; 
                padding: 4px 10px; 
                font-size: 0.75em; 
                font-weight: bold;
                margin-right: 15px;
                border-radius: 5px;
                min-width: 55px;
                text-align: center;
