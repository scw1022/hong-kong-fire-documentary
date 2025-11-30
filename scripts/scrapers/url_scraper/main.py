"""
Extract latest news url from sites into markdown
"""

import glob
import importlib
import os
import sys


def main():
    """"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.append(script_dir)
        
    scrapers_dir = os.path.join(script_dir, "scrapers")
    scraper_files = glob.glob(os.path.join(scrapers_dir, "*.py"))
    
    scrapers = []
    for f in scraper_files:
        filename = os.path.basename(f)
        if filename == "__init__.py":
            continue
            
        module_name = f"scrapers.{filename[:-3]}"
        try:
            print(f"Importing {module_name}...")
            scrapers.append(importlib.import_module(module_name))
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")

    print(f"Found {len(scrapers)} scrapers. Starting scrape...")
    
    for scraper in scrapers:
        try:
            if hasattr(scraper, 'scrape'):
                source, content = scraper.scrape()
                save_as_markdown(source, content)
                print(f"Successfully scraped {source}: {len(content)} articles saved.")
            else:
                print(f"Skipping {scraper.__name__}: No scrape() function.")
        except Exception as e:
            print(f"Error running {scraper.__name__}: {e}")


def save_as_markdown(title: str, content: list[tuple[str, str, str]]) -> None:
    """
    Format string and save as markdown.

    Args:
            title: title of the md file
            content: A list of tuple containing (date, article title, url)

    """

    output_dir = r"output"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)    
    
    if not content:
        print(f"No articles found for {title}. Skipping markdown generation.")
        return

    pre_date: str = sorted(content)[0][0]
    md: str = ""
    md += f"# {title}\n\n"
    md += f"### {pre_date}\n"
    md += "| links |\n| --- |\n"

    for i in sorted(content):
        if pre_date != i[0]:
            pre_date = i[0]
            md += f"### {i[0]}"
            md += "\n| links |\n| --- |\n"
        md += f"| [{i[1]}]({i[2]}) |\n"

    with open(os.path.join(output_dir, f"{title}.md"), "w", encoding="utf-8") as f:
        f.write(md)


if __name__ == "__main__":
    main()
