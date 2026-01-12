from playwright.sync_api import sync_playwright
from time import sleep
import re
LOGIN_URL = "https://www.facebook.com/"
CODE1_URL = "https://2fa.cn/"

EMAIL = "amine.louizi.1@outlook.com"
PASSWORD = "louizi.1@outlook"
CODE = "N6ZZ WFDP VB5C UESX MWX5 RKBQ 7JY6 PZBK"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
    channel="chrome",
    headless=False
                    )
        page = browser.new_page()
     # ===============================
        # 2️⃣ ZU CODE1.HTML GEHEN
        # ===============================
        
        page.goto(CODE1_URL, wait_until="domcontentloaded")

        sleep(8)
        # Code in erstes Feld einfügen
        page.fill("#listToken", CODE)
        page.click("#submit")
        sleep(8)
        # ===============================
        # 3️⃣ GENERIERTEN CODE LESEN
        # ===============================
        # optional: warten bis generatedCode wirklich gefüllt ist
        page.wait_for_function("() => document.querySelector('#output')?.value?.trim().length > 0")

        # VALUE lesen (nicht inner_text)
        out = page.input_value("#output").strip()
        print("OUTPUT:", out)

        last6 = out[-6:] 
        print("OUTPUT2:", last6)

        
        # ===============================
        # 1️⃣ LOGIN.HTML
        # ===============================
        page.goto(LOGIN_URL)
 
                # warten bis Cookie-Dialog da ist
        page.wait_for_selector("text=Decline optional cookies", timeout=15000)
        sleep(2)
        # klicken   
        page.click("text=Decline optional cookies")         
        sleep(2)
        page.evaluate("window.scrollBy(0, 200)")

        page.click("#email")
        sleep(2)
        page.type("#email", EMAIL, delay=140)      # 120ms pro Zeichen

        page.click("#pass")
        sleep(4)
        page.type("#pass", PASSWORD, delay=170)
        sleep(1)
        page.get_by_role("button", name="Log in").click()

        # ✅ HIER: warten bis Navigation fertig ist (oder URL ändert)
        # Wenn du weißt, wie die nächste Seite heißt, setz sie hier rein:
        # page.wait_for_url("**/login_step2.html")
        page.wait_for_load_state("networkidle")
        # ✅ HIER: URL der "gekommenen Seite" speichern
        page.wait_for_load_state("domcontentloaded")
        sleep(5)
        
        page.locator("input[type='text']").first.fill(last6)
        sleep(5)
        page.get_by_role("button", name="Continue").click()

        page.wait_for_timeout(3000)
        sleep(10000)
        browser.close()

if __name__ == "__main__":
    main()
