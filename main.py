import os
import re
import math
import urllib.parse
import smtplib
from email.mime.text import MIMEText
import requests

# ==========================================
# 1. ENVIRONMENT VARIABLES & SECRETS
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
BLOGGER_EMAIL = os.getenv("BLOGGER_EMAIL")
WHATSAPP_PHONE_NUMBER = os.getenv("WA_PHONE")
TEXTMEBOT_API_KEY = os.getenv("TMB_KEY")
BLOG_LANGUAGE = os.getenv("BLOG_LANG", "HINDI")


# ==========================================
# 2. BACKUP EMAIL ALERT ENGINE
# ==========================================
def send_backup_email_alert(title, topic, error_msg):
    try:
        subject = f"⚠️ Blog Published (WhatsApp Failed): {title}"
        body = f"""
Blog publish ho gaya hai but WhatsApp alert fail ho gaya.

Title: {title}
Topic: {topic}
Error: {error_msg}
"""
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)

    except Exception as e:
        print("Email fallback failed:", e)


# ==========================================
# 3. WHATSAPP ALERT
# ==========================================
def send_whatsapp_alert(title, read_time, topic):
    msg = f"""🚀 New Blog Post!

Title: {title}
Topic: {topic}
Read Time: {read_time} min
"""
    encoded = urllib.parse.quote(msg)

    url = f"https://api.textmebot.com/send.php?recipient={WHATSAPP_PHONE_NUMBER}&apikey={TEXTMEBOT_API_KEY}&text={encoded}"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200 or "ERR" in resp.text:
            send_backup_email_alert(title, topic, resp.text)
    except Exception as e:
        send_backup_email_alert(title, topic, str(e))


# ==========================================
# 4. GEMINI GENERATOR
# ==========================================
def generate_blog_content():
    prompt = (
        f"Write a SEO optimized blog in {BLOG_LANGUAGE}. "
        "Use HTML tags <h1>, <h2>, <p>. First line must be <h1> title."
    )

    # ✅ FIXED URL (NO markdown)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    raw_text = data['candidates'][0]['content']['parts'][0]['text']

    title_match = re.search(r'<h1>(.*?)</h1>', raw_text, re.DOTALL)
    if title_match:
        title = title_match.group(1)
        body = re.sub(r'<h1>.*?</h1>', '', raw_text, count=1)
    else:
        title = "Auto Blog"
        body = raw_text

    return title.strip(), body.strip()


# ==========================================
# 5. IMAGE GENERATOR
# ==========================================
def get_featured_image(topic):
    prompt_encoded = urllib.parse.quote(topic)

    # ✅ FIXED URL
    image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=450"

    return f'<img src="{image_url}" style="width:100%;">'


# ==========================================
# 6. BLOGGER PUBLISH
# ==========================================
def publish_to_blogger(title, html):
    msg = MIMEText(html, 'html')
    msg['Subject'] = title
    msg['From'] = GMAIL_USER
    msg['To'] = BLOGGER_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)


# ==========================================
# MAIN
# ==========================================
def main():
    title, body = generate_blog_content()

    words = len(re.sub(r'<[^>]+>', '', body).split())
    read_time = max(1, math.ceil(words / 200))

    image = get_featured_image(title)

    final = image + f"<p>Reading Time: {read_time} min</p>" + body

    publish_to_blogger(title, final)

    send_whatsapp_alert(title, read_time, title)

    print("✅ Done!")


if __name__ == "__main__":
    main()