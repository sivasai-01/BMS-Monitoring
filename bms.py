import time
import requests
from playwright.sync_api import sync_playwright

BMS_URL = "https://in.bookmyshow.com/movies/hyderabad/project-hail-mary/buytickets/ET00492371/20260410"
NTFY_URL = "https://ntfy.sh/mytopic"


def send_notification():
    requests.post(
        NTFY_URL,
        data="🎟 Tickets Released for FRI 10 APR! Hurry up fast 😀".encode("utf-8")
    )


def check_ticket():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )

            page = context.new_page()
            print("Opening page...")
            page.goto(BMS_URL, wait_until="domcontentloaded", timeout=60000)

            # Retry loop (similar to Selenium logic)
            for i in range(30):
                result = page.evaluate("""
                    () => {
                        const parent = document.querySelector('div[id="20260410"]');
                        if (!parent) return "NO_TARGET";

                        const children = Array.from(parent.children);
                        const el = children.find(c => c.innerText.trim() === '10');
                        if (!el) return "NO_TEXT";

                        return window.getComputedStyle(el).color;
                    }
                """)

                print(f"Attempt {i+1}: {result}")

                if result not in ["NO_TARGET", "NO_TEXT"]:
                    browser.close()
                    if result.strip() in ["rgb(51, 51, 51)", "rgb(255, 255, 255)"]:
                        return True
                    return False

                time.sleep(1)

            print("❌ Date never loaded")
            browser.close()
            return False

    except Exception as e:
        print("❌ Error:", e)
        return False


print("Checking ticket availability...")
try:
    if check_ticket():
        print("✅ Tickets Released!")
        send_notification()
    else:
        print("❌ Still not released")
except Exception as e:
    print("Error:", e)
