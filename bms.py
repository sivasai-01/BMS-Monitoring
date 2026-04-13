import time
import requests
from playwright.sync_api import sync_playwright

BMS_URL = "https://in.bookmyshow.com/movies/hyderabad/project-hail-mary/buytickets/ET00492371/20260414"
NTFY_URL = "https://ntfy.sh/mytopic"

# Target date details
TARGET_DAY = "Tue"
TARGET_DATE = "14"
TARGET_MONTH = "Apr"


def send_notification():
    requests.post(
        NTFY_URL,
        data=f"🎟 Tickets Released for {TARGET_DAY.upper()} {TARGET_DATE} {TARGET_MONTH.upper()}! Hurry up fast 😀".encode("utf-8")
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

            # Wait for the date strip to appear
            # page.wait_for_selector("span", timeout=15000)

            for i in range(30):
                result = page.evaluate(
                        """
                        (params) => {
                            const { dayText, dateText, monthText } = params;

                            // Normalize target values
                            const targetDay = dayText.toLowerCase();
                            const targetDate = dateText.trim();
                            const targetMonth = monthText.toLowerCase();

                            // Select all possible date containers
                            const containers = Array.from(document.querySelectorAll("div"));

                            for (const container of containers) {
                                // Select both span and div children
                                const children = container.querySelectorAll(":scope > span, :scope > div");
                                if (children.length !== 3) continue;

                                const day = children[0].innerText.trim().toLowerCase();
                                const date = children[1].innerText.trim();
                                const month = children[2].innerText.trim().toLowerCase();

                                if (
                                    day === targetDay &&
                                    date === targetDate &&
                                    month === targetMonth
                                ) {
                                    const style = window.getComputedStyle(container);
                                    const cursor = style.cursor;

                                    if (cursor === "pointer") return "AVAILABLE";
                                    if (cursor === "not-allowed") return "NOT_AVAILABLE";

                                    return "UNKNOWN";
                                }
                            }

                            return "NO_TARGET";
                        }
                        """,
                        {
                            "dayText": TARGET_DAY,
                            "dateText": TARGET_DATE,
                            "monthText": TARGET_MONTH
                        }
                    )
                print(f"Attempt {i+1}: {result}")

                if result == "AVAILABLE":
                    browser.close()
                    return True
                elif result == "NOT_AVAILABLE":
                    browser.close()
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
