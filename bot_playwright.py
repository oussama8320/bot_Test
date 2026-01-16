from playwright.async_api import async_playwright
from time import sleep
import re
import random
import csv
import asyncio




LOGIN_URL = "https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2F61577308544616%2F"
CODE1_URL = "https://2fa.cn/"


import asyncio
import random
import re

async def process_account(page, email, password, code):
    # ===============================
    # 1️⃣ LOGIN.HTML
    # ===============================
    await page.goto(LOGIN_URL)

    # Warten bis Cookie-Dialog da ist
    try:
        await page.wait_for_selector("text=Decline optional cookies", timeout=15000)
        await asyncio.sleep(2)
        await page.click("text=Decline optional cookies") 
    except:
        print(f"[{email}] Cookie banner not found or already gone.")
        
    await asyncio.sleep(2)
    await page.evaluate("window.scrollBy(0, 90)")

    await page.click("#email")
    await asyncio.sleep(2)
    await page.type("#email", email, delay=140)

    await page.click("#pass")
    await asyncio.sleep(4)
    await page.type("#pass", password, delay=170)
    await asyncio.sleep(1)
    
    # Trigger login
    await page.get_by_role("button", name="Log in").click()

    # Warten bis DOM geladen ist
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(5)
    
    saved_url = page.url
    print(f"✅ [{email}] Gespeicherte URL: {saved_url}")

    # ===============================
    # 2️⃣ ZU CODE1.HTML GEHEN
    # ===============================
    await asyncio.sleep(7)
    await page.goto(CODE1_URL, wait_until="domcontentloaded")

    await asyncio.sleep(8)
    await page.fill("#listToken", code)
    await page.click("#submit")
    await asyncio.sleep(8)

    # ===============================
    # 3️⃣ GENERIERTEN CODE LESEN
    # ===============================
    await page.wait_for_function(
        "() => document.querySelector('#output')?.value?.trim().length > 0"
    )

    out = await page.input_value("#output")
    out = out.strip()
    print(f"[{email}] OUTPUT: {repr(out)}")

    digits = re.findall(r"\d+", out)
    if not digits:
        print(f"❌ [{email}] No digits found in output!")
        return

    last6 = digits[-1][-6:]
    print(f"[{email}] LAST6: {last6}")

    # ===============================
    # 4️⃣ ZURÜCK ZU gespeicherter URL
    # ===============================
    await page.goto(saved_url)
    await page.wait_for_load_state("domcontentloaded")
    
    # Input the code
    inputs = page.locator("input[type='text']")
    await inputs.first.type(last6, delay=200)
    
    await asyncio.sleep(4)
    await page.click("text=Continue")
    await asyncio.sleep(15)

    await page.mouse.click(500, 400)
    await asyncio.sleep(10)

    await page.get_by_role(
        "button",
        name=re.compile("confirm|confirmer", re.I)
    ).click()

    await asyncio.sleep(5)
    btn = page.locator("div[role='button'][aria-haspopup='menu']").first
    await btn.wait_for(state="visible", timeout=100000)
    await btn.click()

    await asyncio.sleep(2)
    await page.locator("div[role='menuitem'][tabindex='0']").first.click()

    await page.locator(
        "div[role='button']",
        has_text=re.compile(r"(Quelque chose à propros|Something about this Page)", re.IGNORECASE)
    ).click()

    await asyncio.sleep(2)
    await page.get_by_role(
        "button",
        name=re.compile(
            r"(Arnaque, fraude ou fausses informations|Scam, fraud or false information)",
            re.IGNORECASE
        )
    ).click()

    await asyncio.sleep(3)
    
    CHOICES = {
        "fraud": ["Fraude ou arnaque", "Fraud or scam"],
        "false_info": ["Partage de fausses informations", "Sharing false information"],
        "spam": ["Spam"],
    }

    key = random.choice(list(CHOICES.keys()))
    labels = CHOICES[key]
    print(f"[{email}] Gewählter Grund: {key}")

    clicked = False
    for label in labels:
        btn_choice = page.get_by_role("button", name=re.compile(label, re.I))
        if await btn_choice.count() > 0:
            await btn_choice.first.click()
            clicked = True
            break

    if not clicked:
        print(f"❌ [{email}] Kein passender Button (FR/EN) gefunden")
    else:
        await asyncio.sleep(4)
        if key == "fraud":
            await page.get_by_role("button", name=re.compile(r"(Envoyer|Submit)", re.I)).click()
            await asyncio.sleep(4)
            await page.get_by_role("button", name=re.compile(r"(Suivant|Next)", re.I)).click()
            await asyncio.sleep(4)
            await page.get_by_role("button", name=re.compile(r"(Terminé|Done)", re.I)).click()
        else:
            await page.get_by_role("button", name=re.compile(r"(Terminé|Done)", re.I)).click()

    await page.wait_for_timeout(3000)
    await asyncio.sleep(5)
async def main():
    # Load accounts
    with open('testo.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        accounts = list(reader)

    async with async_playwright() as p:
        # Launch browser once
        browser = await p.chromium.launch(headless=False, channel="chrome")

        # Process in batches of 3
        for i in range(0, len(accounts), 3):
            batch = accounts[i:i+3]
            tasks = []
            contexts = [] # Keep track of contexts to close them later

            for account in batch:
                # 🛠️ CRITICAL: Create a NEW context for EVERY account
                # This prevents session/cookie sharing
                context = await browser.new_context()
                contexts.append(context)
                
                page = await context.new_page()
                
                tasks.append(process_account(
                    page, 
                    account['email'], 
                    account['password'], 
                    account['code']
                ))

            # Run all 3 accounts in parallel
            await asyncio.gather(*tasks)
            
            # Clean up: Close all contexts in this batch before moving to the next 3
            for ctx in contexts:
                await ctx.close()
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
