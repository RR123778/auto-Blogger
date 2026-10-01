import os
import sys
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from requests.exceptions import RequestException

# Configurable Timeout & Retry Settings
API_TIMEOUT = 180  
MAX_RETRIES = 3


def generate_blog_content():
    gemini_key = os.getenv("GEMINI_KEY")
    if not gemini_key:
        raise ValueError("❌ GEMINI_KEY environment variable missing!")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}

    # Gemini Prompt asking for both unique title and raw HTML body
    prompt = (
        "You are an expert SEO blog writer. Write a detailed, SEO-optimized blog post in Hindi about Personal Finance & Money Management. "
        "Provide your output in valid clean HTML format. "
        "Use <h2>, <h3>, <p>, <ul>, and <li> tags properly. "
        "Do NOT surround the output in markdown code blocks like ```html. Output MUST be pure clean HTML only."
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    print("🔍 [DEBUG] Sending request to Gemini API...")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=API_TIMEOUT
            )
            
            # Authorization / Bad Request Error Check (No retry for 400/401)
            if response.status_code in [400, 401, 403]:
                raise ValueError(f"❌ API Client Error ({response.status_code}): {response.text}")

            response.raise_for_status()
            data = response.json()

            # Safe Parsing of API Response
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError(f"No candidates returned by API: {data}")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts or "text" not in parts[0]:
                raise ValueError(f"Invalid or empty response structure from API: {data}")

            body_html = parts[0]["text"]

            # Dynamic subject line with topic
            title = "पर्सनल फाइनेंस और मनी मैनेजमेंट: सही तरीका और आसान टिप्स"
            category_used = "Finance"

            return title, body_html, category_used

        except RequestException as e:
            print(f"⚠️ [Attempt {attempt}/{MAX_RETRIES}] Request failed: {e}")
            if attempt == MAX_RETRIES:
                print("❌ [ERROR] Max retries reached. Failing process...")
                raise
            sleep_time = 5 * attempt
            print(f"🔄 Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)


def publish_via_email(title, content_html):
    """Publish blog post using Blogger's Mail-to-Blogger feature via Gmail SMTP"""
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_PASS")
    blogger_email = os.getenv("BLOGGER_EMAIL")

    if not all([gmail_user, gmail_pass, blogger_email]):
        print("⚠️ [SKIP] Email credentials incomplete. Cannot auto-publish via Email.")
        return False

    print("📧 [System] Sending post to Blogger via Email...")

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = blogger_email
    msg['Subject'] = title

    # Attach post as HTML content
    msg.attach(MIMEText(content_html, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)
        server.quit()
        print("🎉 [SUCCESS] Post successfully published to Blogger via Email!")
        return True
    except Exception as e:
        print(f"❌ [ERROR] Failed to send email to Blogger: {e}")
        return False


def main():
    print("==========================================")
    print("🔍 [DEBUG] Step 1: Checking Environment Variables...")
    print(f"👉 GEMINI_KEY Present: {bool(os.getenv('GEMINI_KEY'))}")
    print(f"👉 GMAIL_USER: {os.getenv('GMAIL_USER')}")
    print(f"👉 GMAIL_PASS Present: {bool(os.getenv('GMAIL_PASS'))}")
    print(f"👉 BLOGGER_EMAIL: {os.getenv('BLOGGER_EMAIL')}")
    print(f"👉 BLOG_LANG: {os.getenv('BLOG_LANG', 'HINDI')}")
    print("==========================================")
    print("🚀 [System] Starting Auto SEO Blog Publisher...")

    try:
        # Step 1: Content Generation
        title, body_html, category_used = generate_blog_content()
        print("✅ Content generated successfully!")
        print(f"📌 Generated Title: {title}")
        print(f"📂 Category Used: {category_used}")

        # Step 2: Publishing
        publish_via_email(title, body_html)

    except Exception as e:
        print(f"❌ Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
