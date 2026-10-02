import json
import os
import random
import re
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
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

    # Multiple Categories List
    categories = [
        "Personal Finance & Money Management",
        "Fashion & Style Trends",
        "Technology & Gadgets",
        "Online Earning & Freelancing",
    ]

    # Pick a random category per execution
    chosen_category = random.choice(categories)

    # Policy Safe Unsplash Background Images for Featured Image
    category_images = {
        "Personal Finance & Money Management": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1200&h=630&fit=crop",
        "Fashion & Style Trends": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&h=630&fit=crop",
        "Technology & Gadgets": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&h=630&fit=crop",
        "Online Earning & Freelancing": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&h=630&fit=crop",
    }

    featured_image_url = category_images.get(
        chosen_category,
        "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1200&h=630&fit=crop",
    )

    # Enhanced Gemini Prompt with Facebook Policy Safeguards
    prompt = (
        f"You are an expert SEO blog writer. Pick a UNIQUE, informative subtopic under the domain '{chosen_category}' in Hindi.\n"
        "Do NOT write a general overview post. Choose a specific, realistic, high-intent topic every single time.\n\n"
        "FACEBOOK & GOOGLE POLICY RULES (VERY IMPORTANT):\n"
        "1. DO NOT use clickbait, exaggerated financial claims, or fake guarantees (e.g., 'Ghar Baithe Lakhon Kamayein', '100% Free Money', 'Zero Risk Investment').\n"
        "2. Keep the tone educational, professional, and authentic.\n"
        "3. Avoid sensitive/banned trigger keywords related to gambling, quick schemes, or deceptive content.\n\n"
        "Return your response STRICTLY in a valid raw JSON object matching this structure:\n"
        "{\n"
        '  "title": "A compelling, informative Hindi blog title without spammy words",\n'
        f'  "category": "{chosen_category}",\n'
        '  "body_html": "Detailed SEO blog post in clean HTML using <h2>, <h3>, <p>, <ul>, <li> tags properly."\n'
        "}\n\n"
        "Constraints:\n"
        "1. Output ONLY raw valid JSON text.\n"
        "2. Do NOT use markdown code block fences like ```json or ```.\n"
        "3. Properly escape all internal quotes inside HTML attributes."
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    print(
        f"🔍 [DEBUG] Requesting Gemini API for a post under domain: {chosen_category}..."
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=API_TIMEOUT
            )

            if response.status_code in [400, 401, 403]:
                raise ValueError(
                    f"❌ API Client Error ({response.status_code}): {response.text}"
                )

            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError(f"No candidates returned by API: {data}")

            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts or "text" not in parts[0]:
                raise ValueError(
                    f"Invalid or empty response structure from API: {data}"
                )

            raw_text = parts[0]["text"].strip()

            # Clean markdown code blocks if present
            cleaned_json = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                raw_text,
                flags=re.MULTILINE | re.DOTALL,
            ).strip()

            # Parse JSON safely
            parsed_data = json.loads(cleaned_json, strict=False)

            title = parsed_data.get("title", "ट्रेंडिंग ब्लॉग पोस्ट")
            category_used = parsed_data.get("category", chosen_category)
            body_html = parsed_data.get("body_html", "")

            if not body_html:
                raise ValueError("Parsed JSON contains empty 'body_html'")

            # Inject a Facebook-safe featured image at the top of the post HTML
            featured_image_html = f'<div style="text-align: center; margin-bottom: 20px;"><img src="{featured_image_url}" alt="{title}" style="max-width:100%; height:auto; border-radius:8px;" /></div>\n'
            final_html_body = featured_image_html + body_html

            return title, final_html_body, category_used

        except (RequestException, json.JSONDecodeError, ValueError) as e:
            print(
                f"⚠️ [Attempt {attempt}/{MAX_RETRIES}] Request/Parsing failed: {e}"
            )
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
        print(
            "⚠️ [SKIP] Email credentials incomplete. Cannot auto-publish via Email."
        )
        return False

    print("📧 [System] Sending post to Blogger via Email...")

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = blogger_email
    msg["Subject"] = title

    # Attach post as HTML content
    msg.attach(MIMEText(content_html, "html", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
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
