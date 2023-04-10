import requests
import io
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

QUERY = 'https://www.google.com/search?q=tesla&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiki8jeyJ3-AhUQhFwKHdB_A_YQ_AUoAnoECAEQBA&biw=1200&bih=764&dpr=2#imgrc=qEsPqWpoPaXxLM'

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def get_urls(driver, query, delay, max_images):
    '''get a list of sources of images'''
    def scroll_down(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    
    image_urls = set()
    skips = 0

    driver.get(query)

    # Reject cookies
    try:
        driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Reject all"]').click()
    except Exception as error:
        print('There was not cookies argeement, or reject button css has changed')
        print(error)

    # get a list of thumbnails and scroll down to get more images 
    # until reqired amount of images wouldn't collect
    while len(image_urls) + skips < max_images:
        scroll_down(driver)

        thumbnails = driver.find_elements(By.CLASS_NAME, 'Q4LuWd')

        # go through thumbnails and get an src of larger images 
        for img in thumbnails[len(image_urls) + skips:max_images]:
            try:
                img.click()
                time.sleep(delay)
            except:
                continue

            images = driver.find_elements(By.CLASS_NAME, 'iPVvYb')
            for image in images:
                # skip duplicates
                if image.get_attribute('src') in image_urls:
                    max_images += 1
                    skips += 1
                    break
                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    image_urls.add(image.get_attribute('src'))
                    print(f"Found {len(image_urls)}")

    return image_urls



def download_image(url, download_path = '', file_name = 'output.jpg'):
    '''download an image from given url to given path '''
    try:
        # <class 'bytes'>
        image_content = requests.get(url, timeout=10).content
        # <class '_io.BytesIO'>
        image_file = io.BytesIO(image_content)
        # <class 'PIL.JpegImagePlugin.JpegImageFile'>
        image = Image.open(image_file)
        file_path = download_path + file_name

        with open(file_path, 'wb') as f:
            image.save(f, 'JPEG')

        print('Success')
    except Exception as error:
        print('FAILED - ', error)


urls = get_urls(driver, QUERY, 1.3, 7)
for i, url in enumerate(urls):
    download_image(url, 'output/',str(i) + '.jpg')

driver.quit()
