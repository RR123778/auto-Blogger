import smtplib
import json
import urllib.parse
import requests
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==========================================
# 1. CONFIGURATION (GitHub Secrets Use Karenge)
# ==========================================
# AI Settings
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")

# Blogger Email Settings (Gmail)
SENDER_GMAIL = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_PASS") # 16-digit app password
BLOGGER_SECRET_EMAIL = os.environ.get("BLOGGER_EMAIL") # Secret word email

# WhatsApp Notification Settings (TextMeBot)
WHATSAPP_PHONE_NUMBER = os.environ.get("WA_PHONE") # E.g., 91XXXXXXXXXX
TEXTMEBOT_API_KEY = os.environ.get("TMB_KEY") # TextMeBot Trial/Permanent Key

# Language Setting: "HINDI" or "ENGLISH"
# Github me schedule karte waqt change kar sakte hain
LANGUAGE_MODE = os.environ.get("BLOG_LANG", "HINDI")

# Default Topic to Generate (Fallback)
TARGET_TOPIC = "Future Trends in AI by 2030"

# ==========================================
# 2. GEMINI CONTENT GENERATION ENGINE
# ==========================================
def generate_blog_content(topic, language_mode):
    print(f"-> Generating Blog Content in {language_mode} mode...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    if language_mode.upper() == "HINDI":
        lang_instruction = "Language Requirement: Pure, standard, fluent Hindi in Devanagari script. Do not use English words in Roman script."
    else:
        lang_instruction = "Language Requirement: High-quality, clear, fluent English."

    prompt = f"""
    Write a detailed, long-form, engaging, and highly informative blog post about: "{topic}".
    
    {lang_instruction}

    Writing Rules:
    - Include interesting headings (H2, H3).
    - Tone: Conversational, expert, human-like. No generic AI clichés.
    - Output format MUST be valid JSON.

    Output structure ONLY:
    {{
        "title": "SEO Catchy Title",
        "image_prompt": "High-quality detailed English prompt for AI image depicting this topic, cinematic style, no text",
        "content_html": "Full blog body HTML (starting with <h2>, <h3>, <p>, <ul>, <li> tags)"
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Gemini API Error: {response.text}")
            
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        return json.loads(raw_text.strip())
    except Exception as e:
        print(f"ERROR generating content: {e}")
        return None

# ==========================================
# 3. EMAIL TO BLOGGER (PUBLISH)
# ==========================================
def send_email_to_blogger(subject, html_content):
    print("-> Emailing to Blogger Secret Address...")
    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_GMAIL
    msg["To"] = BLOGGER_SECRET_EMAIL
    msg["Subject"] = subject

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_GMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(SENDER_GMAIL, BLOGGER_SECRET_EMAIL, msg.as_string())
        server.close()
        print("✅ Email successfully sent to Blogger!")
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

# ==========================================
# 4. WHATSAPP NOTIFICATION ENGINE (TEXTMEBOT)
# ==========================================
def send_whatsapp_alert(title, language_mode):
    print("-> Sending WhatsApp Notification via TextMeBot...")
    # TextMeBot uses a GET request format
    message_text = f"🚀 *New Blog Published on Blogger!*\n\n*Title:* {title}\n*Language:* {language_mode}\n*Status:* Published Live via Email"
    encoded_message = urllib.parse.quote(message_text)
    
    url = f"https://api.textmebot.com/send.php?recipient={WHATSAPP_PHONE_NUMBER}&apikey={TEXTMEBOT_API_KEY}&text={encoded_message}"
    
    try:
        response = requests.get(url)
        # Check if TextMeBot confirms Success in response body
        if response.status_code == 200 and "Success" in response.text:
            print("📱 WhatsApp Notification Sent Successfully!")
        else:
            print(f"⚠️ Failed to send WhatsApp message (TextMeBot response): {response.text}")
    except Exception as e:
        print(f"❌ TextMeBot API Error: {e}")

# ==========================================
# 5. MAIN PIPELINE
# ==========================================
def run_auto_agent():
    print(f"--- Starting Auto Blogger Agent [{LANGUAGE_MODE} MODE] ---")
    
    # 1. Content Generation
    data = generate_blog_content(TARGET_TOPIC, LANGUAGE_MODE)
    if not data:
        return # Generation failed

    # 2. Free AI Featured Image Generation (Pollinations.ai)
    encoded_prompt = urllib.parse.quote(data["image_prompt"])
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&nologo=true"
    
    image_html = f'<div style="text-align: center; margin-bottom: 20px;"><img src="{image_url}" alt="{data["title"]}" style="max-width:100%; height:auto; border-radius:8px;" /></div><br/>'
    full_html = image_html + data["content_html"]

    # 3. Publish to Blogger
    success = send_email_to_blogger(data["title"], full_html)

    # 4. WhatsApp Notification
    if success:
        send_whatsapp_alert(data["title"], LANGUAGE_MODE)
        print("\n🎉 ALL TASKS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_auto_agent()
