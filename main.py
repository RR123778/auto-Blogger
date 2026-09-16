import smtplib
import json
import urllib.parse
import requests
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 1. CONFIGURATION
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
SENDER_GMAIL = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_PASS")
BLOGGER_SECRET_EMAIL = os.environ.get("BLOGGER_EMAIL")
WHATSAPP_PHONE_NUMBER = os.environ.get("WA_PHONE")
TEXTMEBOT_API_KEY = os.environ.get("TMB_KEY")
LANGUAGE_MODE = os.environ.get("BLOG_LANG", "HINDI")

TARGET_TOPIC = "Future Trends in Artificial Intelligence"

# 2. GEMINI ENGINE
def generate_blog_content(topic, language_mode):
    print(f"-> Generating Blog Content in {language_mode} mode...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    lang_instruction = "Language Requirement: Pure Hindi in Devanagari script." if language_mode.upper() == "HINDI" else "Language Requirement: Fluent English."

    prompt = f"""
    Write an SEO blog post about: "{topic}". {lang_instruction}
    Output format MUST be valid JSON only.
    Structure:
    {{
        "title": "Catchy Title",
        "image_prompt": "Cinematic AI image prompt describing topic, no text",
        "content_html": "Full body HTML with <h2>, <p>, <ul> tags"
    }}
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        if raw_text.startswith("```json"): raw_text = raw_text[7:]
        if raw_text.endswith("```"): raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())
    except Exception as e:
        print(f"ERROR: {e}")
        return None

# 3. EMAIL ENGINE
def send_email_to_blogger(subject, html_content):
    print("-> Emailing to Blogger...")
    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_GMAIL
    msg["To"] = BLOGGER_SECRET_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_GMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(SENDER_GMAIL, BLOGGER_SECRET_EMAIL, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(f"❌ Email Failed: {e}")
        return False

# 4. WHATSAPP ALERT (TextMeBot)
def send_whatsapp_alert(title, language_mode):
    print("-> Sending WhatsApp Notification...")
    text = f"🚀 *New Blog Published!*\n\n*Title:* {title}\n*Language:* {language_mode}"
    url = f"https://api.textmebot.com/send.php?recipient={WHATSAPP_PHONE_NUMBER}&apikey={TEXTMEBOT_API_KEY}&text={urllib.parse.quote(text)}"
    try:
        requests.get(url)
        print("📱 WhatsApp Sent!")
    except Exception as e:
        print(f"❌ WhatsApp Error: {e}")

# 5. MAIN EXECUTION
if __name__ == "__main__":
    data = generate_blog_content(TARGET_TOPIC, LANGUAGE_MODE)
    if data:
        img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(data['image_prompt'])}?width=1200&height=630&nologo=true"
        full_html = f'<div style="text-align:center;"><img src="{img_url}" style="max-width:100%;"/></div><br/>' + data["content_html"]
        if send_email_to_blogger(data["title"], full_html):
            send_whatsapp_alert(data["title"], LANGUAGE_MODE)