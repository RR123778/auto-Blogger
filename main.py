import os
import re
import math
import urllib.parse
import smtplib
from email.mime.text import MIMEText
import requests

# ==========================================
# ENV VARIABLES
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
BLOGGER_EMAIL = os.getenv("BLOGGER_EMAIL")
WA_PHONE = os.getenv("WA_PHONE")
TMB_KEY = os.getenv("TMB_KEY")
BLOG_LANG = os.getenv("BLOG_LANG", "HINDI")


# ==========================================
# GEMINI AI GENERATOR (FIXED)
# ==========================================
def generate_blog_content():
    print("🤖 Generating blog...")

    prompt = f"""
Write a SEO optimized blog in {BLOG_LANG}.
Use HTML tags <h1>, <h2>, <p>.
First line must be title inside <h1>.
"""

    # ✅ FIXED WORKING MODEL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    # 🔥 DEBUG PRINT (very important)
    print("Status:", response.status_code)
    print("Response:", response.text[:500])

    response.raise_for_status()

    data = response.json()

    try:
        raw = data['candidates'][0]['content']['parts'][0]['text']
    except:
        raise Exception("Gemini response format changed / blocked")

    title_match = re.search(r'<h1>(.*?)</h1>', raw, re.DOTALL)

    if title_match:
        title = title_match.group(1)
        body = re.sub(r'<h1>.*?</h1>', '', raw, count=1)
    else:
        title = "Auto Blog"
        body = raw

    return title.strip(), body.strip()


# ==========================================
# IMAGE GENERATOR (FIXED)
# ==========================================
def get_image(topic):
    encoded = urllib.parse.quote(topic)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=450"
    return f'<img src="{url}" style="width:100%;border-radius:8px;">'


# ==========================================
# BLOGGER PUBLISH
# ==========================================
def publish(title, html):
    print("📧 Publishing to Blogger...")

    msg = MIMEText(html, 'html')
    msg['Subject'] = title
    msg['From'] = GMAIL_USER
    msg['To'] = BLOGGER_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)

    print("✅ Blog Sent!")


# ==========================================
# WHATSAPP ALERT
# ==========================================
def send_whatsapp(title, read_time):
    try:
        text = f"🚀 New Blog\n{title}\n⏱ {read_time} min"
        encoded = urllib.parse.quote(text)

        url = f"https://api.textmebot.com/send.php?recipient={WA_PHONE}&apikey={TMB_KEY}&text={encoded}"

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            print("WhatsApp failed:", r.text)

    except Exception as e:
        print("WhatsApp error:", e)


# ==========================================
# MAIN
# ==========================================
def main():
    print("🚀 Starting...")

    title, body = generate_blog_content()

    words = len(re.sub(r'<[^>]+>', '', body).split())
    read_time = max(1, math.ceil(words / 200))

    img = get_image(title)

    final_html = img + f"<p>⏱ Reading Time: {read_time} min</p><hr>" + body

    publish(title, final_html)

    send_whatsapp(title, read_time)

    print("🎉 DONE SUCCESS")


if __name__ == "__main__":
    main()