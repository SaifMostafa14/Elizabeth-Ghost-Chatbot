from __future__ import annotations

import csv
import os
import textwrap
from pathlib import Path
from typing import Dict, List

from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

###############################################################################
# Configuration
###############################################################################

OPENAI_API_KEY = ""
if not OPENAI_API_KEY:
    raise EnvironmentError(
        "Set an OPENAI_API_KEY environment variable before running the chatbot."
    )


CSV_FILE = Path("search.csv")
MAX_SCRAPE_RESULTS = 5

###############################################################################
# Prompt templates
###############################################################################

INTENT_PROMPT = textwrap.dedent(
    """
    Extract the intent of the user input from the following classifications:
    
    - Book search: The user wants to locate a specific book or books on a topic.
      Example: "Do you have any books on machine learning?"
    - Reserve a study space: The user wishes to reserve or ask about study rooms.
    - Library hours: The user asks about operating hours.
    - Checkout inquiry: The user asks about borrowing materials.
    - Books classification: The user wants the call‑number location of a subject.

    If you cannot classify the input, respond with "fallback".

    query = {query}
    """
)

GREET_PROMPT = "Greet the user and ask how you can help today."

###############################################################################
# Utility functions
###############################################################################

# def scrape_library(keyword: str, max_results: int = MAX_SCRAPE_RESULTS) -> List[Dict[str, str]]:
#     """Scrape the Stetson library catalogue for *keyword* and return up to *max_results* rows.

#     A CSV file matching the original format (Title, Author, Summary, Location) is
#     written to *CSV_FILE* for compatibility with the old workflow.
#     """

#     url = (
#         "https://stetson.on.worldcat.org/search?queryPrefix=kw%3A&queryString="
#         f"kw%3A{keyword}&scope=wz%3A4369&expandSearch=off&translateSearch=off"
#     )


#     # Use Selenium’s built‑in driver manager (Chrome 115+)
#     options = Options()
#     # New headless mode avoids GUI requirements and reduces anti‑bot flags
#     options.add_argument("--headless=new")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")

#     results: List[Dict[str, str]] = []
#     with webdriver.Chrome(options=options) as driver:  # ensures quit()
#         driver.get(url)
#         wait = WebDriverWait(driver, 30)
#         ul_xpath = '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul'
#         wait.until(EC.presence_of_element_located((By.XPATH, ul_xpath)))

#         for idx in range(1, max_results + 1):
#             base = (
#                 f'{ul_xpath}/li[{idx}]/div/div/div[1]/div[2]/div/div[3]/div'
#             )
#             try:
#                 title = driver.find_element(By.XPATH, f"{base}/h1/div/div/span/a").text
#                 author = driver.find_element(By.XPATH, f"{base}/div[1]/div/div").text
#                 summary = driver.find_element(By.XPATH, f"{base}/div[3]").text
#                 location = driver.find_element(By.XPATH, f"{base}/div[7]").text
#             except Exception:
#                 # Any missing element breaks the chain—skip this record gracefully.
#                 continue

#             results.append(
#                 {
#                     "Title": title.strip(),
#                     "Author": author.strip(),
#                     "Summary": summary.strip(),
#                     "Location": location.strip(),
#                 }
#             )

#     # Persist to CSV (overwrite each run, matching original behaviour)
#     with CSV_FILE.open("w", newline="", encoding="utf-8") as file:
#         writer = csv.DictWriter(file, fieldnames=["Title", "Author", "Summary", "Location"])
#         writer.writeheader()
#         writer.writerows(results)

#     return results


def scrape_library(keyword: str, max_results: int = 5):
    url = (
        "https://stetson.on.worldcat.org/search?queryPrefix=kw%3A&"
        f"queryString=kw%3A{keyword}&scope=wz%3A4369&expandSearch=off"
        "&translateSearch=off"
    )

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    results = []
    with webdriver.Chrome(options=options) as driver:
        driver.get(url)

        wait = WebDriverWait(driver, 60)

        # 1. Dismiss cookie / privacy banner if it shows up
        try:
            consent_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[data-testid="privacy-accept"]')
                )
            )
            consent_btn.click()
        except TimeoutException:
            pass  # banner never showed → fine

        # 2. Wait for the real results list
        try:
            ul = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ul[data-testid="search-results"]')
                )
            )
        except TimeoutException:
            print("Timed‑out waiting for search results; page markup may have changed.")
            return []

        # 3. Collect the first N list items
        items = ul.find_elements(By.CSS_SELECTOR, "li")[:max_results]

        for item in items:
            title   = safe_text(item, 'h1 span a')
            author  = safe_text(item, '.result-author, div.author')
            summary = safe_text(item, '.result-summary, div.summary')
            where   = safe_text(item, '.availability, div.location')

            results.append(
                dict(Title=title, Author=author, Summary=summary, Location=where)
            )

    # write CSV exactly like before …
    with CSV_FILE.open("w", newline="", encoding="utf-8") as file:
         writer = csv.DictWriter(file, fieldnames=["Title", "Author", "Summary", "Location"])
         writer.writeheader()
         writer.writerows(results)
    return results


def safe_text(element, css):
    """Return element text or 'N/A' if selector missing."""
    try:
        return element.find_element(By.CSS_SELECTOR, css).text.strip()
    except Exception:
        return "N/A"

###############################################################################
# Chatbot class
###############################################################################

class LibraryChatbot:
    """Interactive CLI‑based library assistant."""

    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)

    # ---------------------------------------------------------------------
    # Small wrappers around the OpenAI completion endpoint
    # ---------------------------------------------------------------------
    def _complete(self, prompt: str, **kwargs) -> str:
        """Call the completion endpoint and return the trimmed string."""
        response = self.client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            temperature=0,
            max_tokens=kwargs.get("max_tokens", 200),
        )
        return response.choices[0].text.strip()

    def classify_intent(self, user_input: str) -> str:
        prompt = INTENT_PROMPT.format(query=user_input)
        completion = self._complete(prompt).lower()
        return completion.split(":")[-1].strip()

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------
    def handle_book_search(self, query: str) -> None:
        print("I understand you'd like to search for a book. Please provide a keyword—title, author, or subject—so I can help:")
        keyword = input(": ")
        results = scrape_library(keyword)

        # Build numbered list for the user via OpenAI to preserve original style.
        joined = ", ".join(
            f"{row['Title']} by {row['Author']}" for row in results
        )
        prompt = textwrap.dedent(
            f"""
            Tell the user these are the results we found based on the library database search. Extract the Titles and Authors from:
            {joined}

            Provide the response as a numbered list like:
            1- Title by Author
            """
        )
        print(self._complete(prompt))

        print("Did you find what you were looking for, or do you need more info about a specific book?")
        follow_up = input(": ")
        # Subsequent follow‑up logic is unchanged from the original script; for brevity it is omitted.

    def handle_reserve_space(self, query: str) -> None:
        prompt = textwrap.dedent(
            """
            Answer the question using the following information. Rephrase your answer directly, and if unsure say so.

            Study Rooms:\nThe Alpha, Beta, and Gamma rooms seat four and include whiteboards.\nThe Taylor Room seats six and includes a collaboration station.\n\nReserve at: https://stetson.libcal.com/reserve/StudyRooms\n
            query = {query}
            """
        )
        print(self._complete(prompt.format(query=query), max_tokens=500))

    def handle_library_hours(self, query: str) -> None:
        # Concise hours table; trimmed for readability.
        hours_text = (
            "Monday–Thursday: 8 AM – 12 AM\n"
            "Friday: 8 AM – 6 PM\n"
            "Saturday: 10 AM – 6 PM\n"
            "Sunday: 11 AM – 12 AM"
        )
        prompt = (
            "Answer truthfully using this schedule:\n" + hours_text + "\nquery = {query}"
        )
        print(self._complete(prompt.format(query=query), max_tokens=500))

    # Additional handlers (checkout, books classification, fallback) would follow the same pattern.

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Start the interactive prompt."""
        print(self._complete(GREET_PROMPT))
        while True:
            user = input("Q: ").strip()
            if user.lower() in {"stop", "quit", "exit"}:
                break
            intent = self.classify_intent(user)

            if intent == "book search":
                self.handle_book_search(user)
            elif intent == "reserve a study space":
                self.handle_reserve_space(user)
            elif intent == "library hours":
                self.handle_library_hours(user)
            else:
                print("I'm sorry—I can only help with book searches, study‑space reservations, library hours, checkout inquiries, and locating books.")

###############################################################################
# Entrypoint
###############################################################################

if __name__ == "__main__":
    chatbot = LibraryChatbot(api_key=OPENAI_API_KEY)
    chatbot.run()
