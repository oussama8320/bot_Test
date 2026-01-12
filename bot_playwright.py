from playwright.sync_api import sync_playwright
from time import sleep
import re
LOGIN_URL = "https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2F61577308544616%2F"
CODE1_URL = "https://2fa.cn/"

EMAIL = "salhimohammed1@hotmail.com"
PASSWORD = "oussa2013"
CODE = "N6ZZ WFDP VB5C UESX MWX5 RKBQ 7JY6 PZBK"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
    channel="chrome",
    headless=False
                    )
        page = browser.new_page()
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
        page.evaluate("window.scrollBy(0, 90)")

        page.click("#email")
        sleep(2)
        page.type("#email", EMAIL, delay=140)      # 120ms pro Zeichen

        page.click("#pass")
        sleep(4)
        page.type("#pass", PASSWORD, delay=170)
        sleep(1)
        page.get_by_role("button", name="Log in").click()

                # Warten bis DOM geladen ist
        page.wait_for_load_state("domcontentloaded")

        # Warten bis Netzwerk ruhig ist (keine Requests mehr)
        page.wait_for_load_state("networkidle")
        sleep(5)
        # ✅ JETZT ist die Seite komplett geladen → URL speichern
        saved_url = page.url
        print("✅ Gespeicherte URL:", saved_url)

        # ===============================
        # 2️⃣ ZU CODE1.HTML GEHEN
        # ===============================
        sleep(10)
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
        import re

        page.wait_for_function(
            "() => document.querySelector('#output')?.value?.trim().length > 0"
        )

        # VALUE lesen (nicht innerText)
        out = page.input_value("#output").strip()
        print("OUTPUT:", repr(out))

        # 🔍 nur ZIFFERN extrahieren
        digits = re.findall(r"\d+", out)

        # ✅ LETZTE 6 ZIFFERN nehmen
        last6 = digits[-1][-6:]

        print("LAST6:", last6)


        
        # ===============================
        # 4️⃣ ZURÜCK ZU gespeicherter URL
        # ===============================
        # ✅ HIER: zu der gespeicherten URL gehen
        page.goto(saved_url)
        page.wait_for_load_state("domcontentloaded")
        
        page.locator("input[type='text']").first.type(last6, delay=200)
        sleep(8)
        page.click("text=Continue")
        sleep(15)

        page.mouse.click(500, 400)
        sleep(2)
        page.get_by_role("button", name="Toujours confirmer qu’il s’agit de moi").click()

        page.wait_for_timeout(3000)
        sleep(10000)
        browser.close()

if __name__ == "__main__":
    main()
