import requests
from bs4 import BeautifulSoup
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_news():
    # 부동산 관련 핵심 키워드 검색
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
    now_full = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M')
    now_simple = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%m월 %d일')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
        
        <title>Daily「부동산」Picks</title>
        <meta name="description" content="{now_simple} 업데이트된 부동산 핵심 리포트">
        <meta property="og:type" content="website">
        <meta property="og:title" content="Daily「부동산」Picks">
        <meta property="og:description" content="{now_simple} 부동산/아파트/재개발 주요 소식 모음">
        <meta property="og:image" content="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Mouse%20Face.png">
        <meta property="og:image:width" content="800">
        <meta property="og:image:height" content="400">
        <meta name="twitter:card" content="summary_large_image">

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
                box-sizing: border-box;
            }}
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
            .title-area {{ text-align: center; margin-bottom: 15px;
