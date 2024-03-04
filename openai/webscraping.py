from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

def webscraping(keyword):
    # Set up the Selenium webdriver (you'll need to download and install the appropriate webdriver for your browser)
    chrome_path = '/home/smostafa/openai/chromedriver'
    service = Service(executable_path=chrome_path)
    service.start()

    driver = webdriver.Chrome(service=service)

    # Navigate to the URL
    url = "https://stetson.on.worldcat.org/search?queryPrefix=kw%3A&queryString=kw%3A" + keyword + "&scope=wz%3A4369"
    driver.get(url)

    wait = WebDriverWait(driver, 60)  # Maximum wait time in seconds

    book_list_Xpath = '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul'
    book_list_element = wait.until(EC.presence_of_element_located((By.XPATH, book_list_Xpath)))

    # Extract information from the web page
    books = book_list_element.find_elements(By.TAG_NAME, "li")
    print(books)
    
    # Write data to a CSV file
    with open('try.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Author", "Summary", "Available"])

        for i in range(1,6):
            for book in books:
                title_element = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li['+str(i)+']/div/div/div[1]/div[2]/div/div[3]/div/h1/div/div/span/a')
                title = title_element.text.strip()
            #title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.MuiTypography-root.MuiLink-root.MuiLink-underlineAlways.MuiTypography-body1.MuiTypography-colorSecondary')))
            #title = title_element.get_attribute('aria-label')

                author_element = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li['+str(i)+']/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div/div')
                author = author_element.text.strip()

                summary_element = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li['+str(i)+']/div/div/div[1]/div[2]/div/div[3]/div/div[3]')
                summary = summary_element.text.strip()

                available_element = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li['+str(i)+']/div/div/div[1]/div[2]/div/div[3]/div/div[7]')
                available = available_element.text.strip()

#            checkout_status = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li[1]/div/div/div[2]/div[1]/div/div/div/ul/li/div/div/div/div[3]/div/div/div/div[2]/span/p')
#            checkout = checkout_status.text.strip()

            writer.writerow([title, author, summary, available])

    driver.quit()


if __name__ == "__main__":
    webscraping("1984")