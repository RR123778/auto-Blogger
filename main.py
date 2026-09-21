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
# GEMINI BLOG GENERATOR (FINAL FIX)
# ==========================================
def generate_blog_content():
    print("🤖 Generating blog...")

    prompt = f"""
Write a highly engaging SEO optimized blog in {BLOG_LANG}.
Use HTML tags <h1>, <h2>, <p>, <ul>.
First line must be <h1> title.
"""

    # ✅ FINAL CORRECT API (WORKING)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        print("Status:", response.status_code)
        print("Response:", response.text[:300])

        response.raise_for_status()

        data = response.json()
        raw = data['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        raise Exception(f"Gemini API Failed: {e}")

    # Extract title
    title_match = re.search(r'<h1>(.*?)</h1>', raw, re.DOTALL)

    if title_match:
        title = title_match.group(1).strip()
        body = re.sub(r'<h1>.*?</h1>', '', raw, count=1).strip()
    else:
        title = "Auto Blog"
        body = raw

    return title, body


# ==========================================
# IMAGE GENERATOR
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

    print("✅ Blog Sent Successfully!")


# ==========================================
# WHATSAPP ALERT
# ==========================================
def send_whatsapp(title, read_time):
    try:
        text = f"🚀 New Blog Published!\n\n{title}\n⏱ {read_time} min read"
        encoded = urllib.parse.quote(text)

        url = f"https://api.textmebot.com/send.php?recipient={WA_PHONE}&apikey={TMB_KEY}&text={encoded}"

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            print("⚠️ WhatsApp failed:", r.text)

    except Exception as e:
        print("⚠️ WhatsApp error:", e)


# ==========================================
# MAIN
# ==========================================
def main():
    print("🚀 Starting Auto Blogger...")

    title, body = generate_blog_content()

    words = len(re.sub(r'<[^>]+>', '', body).split())
    read_time = max(1, math.ceil(words / 200))

    image = get_image(title)

    final_html = image + f"<p>⏱ Reading Time: {read_time} min</p><hr>" + body

    publish(title, final_html)

    send_whatsapp(title, read_time)

    print("🎉 ALL DONE SUCCESSFULLY!")


if __name__ == "__main__":
    main()