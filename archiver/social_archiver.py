from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime, os

class SocialArchiver:
    def __init__(self, output_dir="data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def archive_page(self, url: str) -> dict:
        options = Options()
        options.add_argument("--headless")
        
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get(url)
        snapshot = {
            "url": url,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "html": driver.page_source,
            "title": driver.title,
        }
        driver.quit()
        filename = f"{self.output_dir}/snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(snapshot["html"])
        print(f"[+] Archived: {url} → {filename}")
        return snapshot