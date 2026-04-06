import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BMS_URL = "https://in.bookmyshow.com/movies/hyderabad/project-hail-mary/buytickets/ET00492371/20260408"
NTFY_URL = "https://ntfy.sh/mytopic"

TARGET_COLOR = "rgb(51, 51, 51)"   # Black → tickets released


def send_notification():
    requests.post(
        NTFY_URL,
        data="🎟 Tickets Released for THU 08 APR! Hurry up fast 😀".encode("utf-8")
    )

def check_ticket():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("Opening page...")
        driver.get(BMS_URL)

        # 🔥 Retry loop (Python side, NOT JS)
        for i in range(30):  # 30 seconds max
            # result = driver.execute_script("""
            #     const nodes = document.querySelectorAll('div[id^="2026"]');

            #     if (!nodes || nodes.length === 0) {
            #         return "NO_DATES";
            #     }

            #     const target = Array.from(nodes).find(e => e.id === "20260408");

            #     if (!target) return "NO_TARGET";

            #     const children = target.querySelectorAll('div');

            #     for (let child of children) {
            #         if (child.innerText.trim() === '08') {
            #             return window.getComputedStyle(child).color;
            #         }
            #     }

            #     return "NO_TEXT";
            # """)

            result = driver.execute_script("""
                const parent = document.querySelector('div[id="20260408"]');

                if (!parent) return "NO_TARGET";

                // get ONLY visible direct children
                const children = Array.from(parent.children);

                // find exact "08" element
                const el = children.find(c => c.innerText.trim() === '08');

                if (!el) return "NO_TEXT";

                const color = window.getComputedStyle(el).color;

                return color;
            """)
            print(f"Attempt {i+1}: {result}")

            if result not in ["NO_DATES", "NO_TARGET", "NO_TEXT"]:
                # 🎯 got actual color
                if result.strip() in ["rgb(51, 51, 51)", "rgb(255, 255, 255)"]:
                    return True
                return False

            time.sleep(1)

        print("❌ Date never loaded")
        return False

    except Exception as e:
        print("❌ Error:", e)
        return False

    finally:
        driver.quit()

# ⏰ Loop every 10 mins
# while True:
print("Checking ticket availability...")

#     try:
#         if check_ticket():
#             print("✅ Tickets Released!")
#             send_notification()
#             break
#         else:
#             print("❌ Still not released")

#     except Exception as e:
#         print("Error:", e)

#     time.sleep(600)  # 10 minutes
try:
    if check_ticket():
        print("✅ Tickets Released!")
        send_notification()
    else:
        print("❌ Still not released")

except Exception as e:
    print("Error:", e)