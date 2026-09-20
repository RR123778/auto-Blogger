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
    print("📧 [Backup Email Engine] Sending fallback email notification...")
    try:
        subject = f"⚠️ [Alert] Blog Published (WhatsApp Failed): {title}"
        body = (
            f"Hello,\n\n"
            f"Aapka blog post successfully publish ho gaya hai, lekin TextMeBot alert fail ho gaya tha.\n\n"
            f"📌 Title: {title}\n"
            f"🎯 Topic: {topic}\n"
            f"⚠️ TextMeBot Error: {error_msg}\n\n"
            f"Status: Published to Blogger\n"
        )
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER  # Apne khud ke Gmail par alert aayega

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print("📧 [Backup Email Engine] Fallback Email alert sent successfully!")
    except Exception as mail_err:
        print(f"⚠️ [Backup Email Engine] Failed to send fallback email: {mail_err}")


# ==========================================
# 3. CRASH-PROOF WHATSAPP ENGINE WITH FALLBACK
# ==========================================
def send_whatsapp_alert(title, read_time, topic):
    print("📱 [WhatsApp Engine] Sending instant alert...")
    msg = (
        f"🚀 *New Blog Post Live!*\n\n"
        f"📌 *Title:* {title}\n"
        f"🎯 *Topic:* {topic}\n"
        f"⏱️ *Read Time:* ~{read_time} min\n"
        f"🌐 *Status:* Published to Blogger"
    )
    encoded = urllib.parse.quote(msg)
    url = f"https://api.textmebot.com/send.php?recipient={WHATSAPP_PHONE_NUMBER}&apikey={TEXTMEBOT_API_KEY}&text={encoded}"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and "ERR" not in resp.text:
            print("📱 [WhatsApp Engine] Alert delivered successfully!")
        else:
            error_details = resp.text
            print(f"⚠️ [WhatsApp Engine] WhatsApp failed! Triggering email fallback... Details: {error_details}")
            send_backup_email_alert(title, topic, error_details)
    except Exception as e:
        print(f"⚠️ [WhatsApp Engine] TextMeBot Error/Down: {e}. Triggering email fallback...")
        send_backup_email_alert(title, topic, str(e))


# ==========================================
# 4. GEMINI AI CONTENT GENERATOR
# ==========================================
def generate_blog_content():
    print("🤖 [Gemini Engine] Generating trending blog post...")
    
    prompt = (
        f"Write a highly engaging, SEO-optimized, comprehensive blog post in {BLOG_LANGUAGE}. "
        "Pick a popular trending topic in AI, tech, online earning, or modern skills. "
        "Structure the output in clean HTML with <h2>, <h3>, <p>, and <ul>/<li> tags. "
        "Do NOT include markdown block markers like ```html. "
        "The first line MUST be the title wrapped inside <h1> tags."
    )
    
    # Clean direct URL String
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=){GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    raw_text = data['candidates'][0]['content']['parts'][0]['text']
    
    # Extract Title
    title_match = re.search(r'<h1>(.*?)</h1>', raw_text, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        body_html = re.sub(r'<h1>.*?</h1>', '', raw_text, count=1, flags=re.IGNORECASE | re.DOTALL).strip()
    else:
        title = "Trending Tech & AI Insights"
        body_html = raw_text

    return title, body_html


# ==========================================
# 5. POLLINATIONS AI IMAGE GENERATOR
# ==========================================
def get_featured_image(topic):
    print("🎨 [Image Engine] Generating featured image via Pollinations.ai...")
    prompt_encoded = urllib.parse.quote(f"hd cinematic concept art of {topic}, vibrant lighting, 8k resolution")
    image_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){prompt_encoded}?width=800&height=450&nologo=true"
    return f'<p><img src="{image_url}" alt="{topic}" style="width:100%; height:auto; border-radius:8px; margin-bottom:20px;"></p>'


# ==========================================
# 6. GMAIL-TO-BLOGGER PUBLISHER ENGINE
# ==========================================
def publish_to_blogger(title, full_html):
    print("📧 [Blogger Engine] Publishing blog via Gmail Secret Address...")
    
    msg = MIMEText(full_html, 'html')
    msg['Subject'] = title
    msg['From'] = GMAIL_USER
    msg['To'] = BLOGGER_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
    
    print("✅ [Blogger Engine] Successfully delivered to Blogger!")


# ==========================================
# MAIN EXECUTION FLOW
# ==========================================
def main():
    print("🚀 [System] Starting Auto Blog Publisher...")
    
    # Step 1: Generate AI Blog
    title, body_html = generate_blog_content()
    
    # Step 2: Calculate Reading Time
    word_count = len(re.sub(r'<[^>]*>', '', body_html).split())
    read_time = max(1, math.ceil(word_count / 200))
    
    # Step 3: Attach Image & Reading Time Badge
    image_html = get_featured_image(title)
    badge_html = f'<p>⏱️ <i>Reading Time: ~{read_time} min</i></p><hr>'
    final_content = image_html + badge_html + body_html
    
    # Step 4: Publish to Blogger
    publish_to_blogger(title, final_content)
    
    # Step 5: Send Notification (TextMeBot with Email Fallback)
    send_whatsapp_alert(title, read_time, title)
    
    print("🎉 [System] All tasks completed successfully!")

if __name__ == "__main__":
    main()