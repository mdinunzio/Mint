import scrapekit
import time


def refresh_accounts_and_kill():
    """
    Refresh Mint accounts then kill the driver.
    """
    ms = scrapekit.MintScraper()
    ms.refresh_accounts()
    time.sleep(15 * 60)
    ms.driver.quit()


def download_and_kill():
    """
    Download Mint transactions then kill the driver.
    """
    ms = scrapekit.MintScraper()
    ms.download_transactions()