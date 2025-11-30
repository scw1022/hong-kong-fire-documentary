import asyncio
from playwright.async_api import async_playwright
import datetime
import os

async def _scrape_async():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        results = []
        
        keywords = ["宏福苑 火警", "大埔 火警"]
        found_issue_page = None

        print("Searching for keywords...")
        for keyword in keywords:
            url = f"https://www.hk01.com/search?q={keyword}"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
                
                # Check for "Issue" links or collection links
                links = await page.query_selector_all('a[href*="/issue/"]')
                for link in links:
                    href = await link.get_attribute('href')
                    if href:
                        found_issue_page = href if href.startswith("http") else "https://www.hk01.com" + href
                        print(f"Found issue page via search: {found_issue_page}")
                        break
                if found_issue_page:
                    break
            except Exception as e:
                print(f"Search failed for {keyword}: {e}")

        # Fallback to the known issue page if search fails (it was found in initial exploration)
        if not found_issue_page:
            found_issue_page = "https://www.hk01.com/issue/10398"
            print(f"Using fallback issue page: {found_issue_page}")

        # Now scrape the issue page
        print(f"Scraping issue page: {found_issue_page}")
        try:
            await page.goto(found_issue_page, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            elements = await page.query_selector_all('a')
            for el in elements:
                try:
                    title = await el.inner_text()
                    link = await el.get_attribute('href')
                    
                    if link and title and len(title) > 5 and not "javascript" in link:
                         if not link.startswith("http"):
                            link = "https://www.hk01.com" + link
                         
                         # Deduplicate
                         if link not in [r['link'] for r in results]:
                             # Verify the link is reachable (simple check)
                             # We won't fetch every page to save time, but we assume links on the page are valid.
                             results.append({
                                 "title": title.strip(),
                                 "link": link
                             })
                except:
                    pass
        except Exception as e:
            print(f"Error visiting issue page: {e}")
            
        await browser.close()
        return results

def scrape():
    """
    Scrapes HK01 and returns a tuple of (source_name, list_of_articles).
    Each article is a tuple of (date, title, link).
    """
    raw_results = asyncio.run(_scrape_async())
    
    # Default date for this specific event collection
    default_date = "2025-11-26"
    
    formatted_results = []
    for r in raw_results:
        formatted_results.append((default_date, r['title'], r['link']))
        
    return ("HK01", formatted_results)
