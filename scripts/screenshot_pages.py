#!/usr/bin/env python3
"""
Auto-Bidder Screenshot Script
Automatically captures screenshots of all pages in the application.
"""
import asyncio
import re
from pathlib import Path
from playwright.async_api import async_playwright, Page

# Configuration
BASE_URL = "http://localhost:3000"
EMAIL = "jxjwilliam@2925.com"
PASSWORD = "William1!"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "assets" / "images"

# Ensure screenshots directory exists
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(text: str) -> str:
    """Convert menu text to a valid filename."""
    # Remove special characters, convert to lowercase, replace spaces with hyphens
    filename = re.sub(r'[^\w\s-]', '', text.lower())
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-')


async def login(page: Page) -> bool:
    """Login to the application."""
    print(f"🔐 Logging in to {BASE_URL}...")

    try:
        await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)

        # Wait for login form
        await page.wait_for_selector('input[type="email"], input[name="email"], input[id*="email"]', timeout=10000)

        # Fill in credentials
        email_input = page.locator('input[type="email"], input[name="email"], input[id*="email"]').first
        await email_input.fill(EMAIL)

        password_input = page.locator('input[type="password"], input[name="password"]').first
        await password_input.fill(PASSWORD)

        # Click login button
        login_button = page.locator('button:has-text("Login"), button:has-text("Sign in"), button[type="submit"]').first
        await login_button.click()

        # Wait for navigation to dashboard
        await page.wait_for_url("**/dashboard**", timeout=10000)
        print("✅ Login successful!")
        return True

    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False


async def discover_menu_items(page: Page) -> list[dict]:
    """Discover all menu items from the left sidebar."""
    print("🔍 Discovering menu items...")

    menu_items = []

    # Wait for sidebar to be visible
    await page.wait_for_timeout(2000)  # Give time for sidebar to render

    # Try multiple selectors for sidebar menu items
    selectors = [
        'nav a',
        'aside a',
        '[role="navigation"] a',
        'nav[class*="sidebar"] a',
        'aside[class*="sidebar"] a',
        'div[class*="sidebar"] a',
    ]

    for selector in selectors:
        try:
            links = await page.locator(selector).all()
            if links:
                print(f"✅ Found {len(links)} potential menu items using selector: {selector}")

                for link in links:
                    try:
                        # Get text content
                        text = await link.text_content()
                        if not text or not text.strip():
                            continue

                        text = text.strip()

                        # Get href
                        href = await link.get_attribute('href')
                        if not href:
                            continue

                        # Skip external links and certain routes
                        if href.startswith('http') and not href.startswith(BASE_URL):
                            continue

                        # Check if it's visible (part of main navigation)
                        is_visible = await link.is_visible()
                        if not is_visible:
                            continue

                        menu_items.append({
                            'text': text,
                            'href': href,
                            'filename': sanitize_filename(text)
                        })

                    except Exception as e:
                        continue

                if menu_items:
                    break  # Found menu items, stop trying other selectors

        except Exception as e:
            continue

    # Remove duplicates based on href
    seen_hrefs = set()
    unique_items = []
    for item in menu_items:
        if item['href'] not in seen_hrefs:
            seen_hrefs.add(item['href'])
            unique_items.append(item)

    print(f"📋 Discovered {len(unique_items)} unique menu items:")
    for item in unique_items:
        print(f"   - {item['text']} → {item['filename']}.png")

    return unique_items


async def take_screenshot(page: Page, menu_item: dict) -> bool:
    """Navigate to a page and take a screenshot."""
    try:
        text = menu_item['text']
        href = menu_item['href']
        filename = menu_item['filename']

        print(f"📸 Capturing '{text}'...")

        # Construct full URL
        if href.startswith('http'):
            url = href
        elif href.startswith('/'):
            url = f"{BASE_URL}{href}"
        else:
            url = f"{BASE_URL}/{href}"

        # Navigate to the page
        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Wait for content to load
        await page.wait_for_timeout(1500)

        # Take screenshot
        screenshot_path = SCREENSHOTS_DIR / f"{filename}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        print(f"   ✅ Saved to {screenshot_path}")
        return True

    except Exception as e:
        print(f"   ❌ Failed to capture '{menu_item['text']}': {e}")
        return False


async def main():
    """Main function to orchestrate the screenshot process."""
    print("=" * 60)
    print("🚀 Auto-Bidder Screenshot Automation")
    print("=" * 60)

    async with async_playwright() as playwright:
        # Launch browser
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
        )
        page = await context.new_page()

        try:
            # Step 1: Login
            if not await login(page):
                print("❌ Cannot proceed without successful login")
                return

            # Step 2: Discover menu items
            menu_items = await discover_menu_items(page)

            if not menu_items:
                print("❌ No menu items found. Please check the sidebar selectors.")
                return

            # Step 3: Take screenshots
            print(f"\n📸 Taking screenshots of {len(menu_items)} pages...")
            print("-" * 60)

            success_count = 0
            for i, menu_item in enumerate(menu_items, 1):
                print(f"\n[{i}/{len(menu_items)}] ", end="")
                if await take_screenshot(page, menu_item):
                    success_count += 1

            # Summary
            print("\n" + "=" * 60)
            print(f"✅ Completed! {success_count}/{len(menu_items)} screenshots captured")
            print(f"📁 Screenshots saved to: {SCREENSHOTS_DIR}")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
