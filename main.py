import time
import pandas as pd
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC


def change_postcode(web_driver):
    # Change post code to access to all products
    WebDriverWait(web_driver, 5).until(EC.presence_of_element_located((By.ID, "glow-ingress-line2")))
    button = web_driver.find_element(By.ID, "glow-ingress-line2")
    button.click()

    WebDriverWait(web_driver, 5).until(EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput_0")))
    box1 = web_driver.find_element(By.ID, 'GLUXZipUpdateInput_0')
    box1.send_keys('120')

    time.sleep(0.1)
    WebDriverWait(web_driver, 5).until(EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput_1")))
    box2 = web_driver.find_element(By.ID, 'GLUXZipUpdateInput_1')
    box2.send_keys('0023')

    time.sleep(0.3)
    WebDriverWait(web_driver, 5).until(EC.presence_of_element_located(
        (By.XPATH, "//span [(@id='GLUXZipUpdate') and (@class='a-button a-button-span12')]")))
    apply_button = web_driver.find_element(
        By.XPATH, "//span [(@id='GLUXZipUpdate') and (@class='a-button a-button-span12')]")
    apply_button.click()

    time.sleep(0.5)
    try:
        WebDriverWait(web_driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.a-popover-footer > span:nth-child(1) > span:nth-child(1) > input:nth-child(1)')))
        continue_button = web_driver.find_element(
            By.CSS_SELECTOR, '.a-popover-footer > span:nth-child(1) > span:nth-child(1) > input:nth-child(1)')
        continue_button.click()
    except Exception as e:
        print(e)


def scroll_until_the_end(web_driver):
    # Scroll the page until the end to search for all products
    liElement = web_driver.find_element(By.ID, 'endOfList')
    while True:
        web_driver.execute_script("arguments[0].scrollIntoView(true);", liElement)
        time.sleep(1)
        try:
            web_driver.find_element(By.XPATH, "// span[contains(text(),'#50')]")
            break
        except Exception as e:
            continue


def init_product_info():
    product_info = {'URL': [], 'Title': [], 'Price': [], 'Rating': [],
                    'Pic1': [], 'Pic2': [], 'Pic3': [], 'Pic4': [], 'Pic5': [], 'Pic6': [], 'Pic7': [],
                    'Pic8': [], 'Pic9': [], 'Product description': []}
    return product_info


def append_url(soup, product_info):
    # Iterate through 50 products and append their url to dictionary
    for a in soup.findAll('a', href=True, attrs={"class": "a-link-normal", 'role': 'link'}):
        landing_link = 'https://www.amazon.co.jp'
        soup_text = str(a)
        if 'tabindex' in soup_text:
            url = landing_link + a.get('href')
            product_info['URL'].append(url)
    return product_info


def update_price_and_title(soup, product_info):
    cond = 0
    for a in soup.findAll('span',
                          attrs={'id': ['productTitle', 'sns-base-price']}):
        text_soup = str(a)
        if 'id="sns-base-price"' in text_soup:
            price = a.text
            product_info['Price'].append(price.strip())
            cond += 1
        elif 'id="productTitle"' in text_soup:
            title = a.text
            product_info['Title'].append(title.strip())
            cond += 1
        if cond == 2:
            break
    else:
        if cond != 2:
            cond = 0
            for a in soup.findAll('span', class_=['a-price-whole', 'a-price-symbol']):
                text_soup = str(a)
                if 'symbol' in text_soup:
                    symbol = a.text
                    cond += 1
                else:
                    whole = a.text
                    cond += 1
                if cond == 2:
                    break
            product_info['Price'].append(symbol + whole)
    return product_info


def update_rating(soup, product_info):
    for a in soup.findAll('span', class_='a-icon-alt'):
        try:
            text_soup = str(a)
            if 'out of 5 stars' in text_soup:
                rating = a.text
                product_info['Rating'].append(rating)
                break
        except AttributeError:
            continue
    return product_info


def update_img(web_driver, product_info):
    img_url = []
    for i in range(4, 14):

        xpath = '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/' \
                'div[1]/div/div/div[1]/ul/li[{}]/span/span/span/input'.format(i)
        xpath1 = '/html/body/div[2]/div[3]/div[3]/div[4]/div[3]/div[1]/' \
                 'div[1]/div/div/div[1]/ul/li[{}]/span/span/span/input'.format(i)
        xpath2 = '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]' \
                 '/div/div/div[1]/ul/li[{}]/span/span/span/input'.format(i)
        xpath3 = '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/' \
                 'div/div/div[1]/ul/li[{}]/span/span/span/input'.format(i)

        try:
            WebDriverWait(web_driver, 0.1).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except Exception as e:
            try:
                WebDriverWait(web_driver, 0.1).until(EC.presence_of_element_located((By.XPATH, xpath1)))
                xpath = xpath1
            except Exception as e:
                try:
                    WebDriverWait(web_driver, 0.1).until(EC.presence_of_element_located((By.XPATH, xpath2)))
                    xpath = xpath2
                except Exception as e:
                    xpath = xpath3

        try:
            action = webdriver.ActionChains(web_driver)
            element = web_driver.find_element(By.XPATH, xpath)
            action.move_to_element(element)
            action.perform()

            img_paths = [
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[1]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[5]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[6]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[7]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[8]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[9]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[10]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[11]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[12]/span/span/div/img',
                '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[1]/span/span/div/img'
                '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[5]/span/span/div/img',
                '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[7]/span/span/div/img',
                '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[8]/span/span/div/img',
                '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[9]/span/span/div/img',
                '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[10]/span/span/div/img',
                '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[6]/span/span/div/img',
                '//*[@id="landingImage"]',
                '/html/body/div[2]/div[3]/div[3]/div[4]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[5]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[3]/div[4]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[6]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[3]/div[4]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[7]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[3]/div[4]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[8]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[3]/div[4]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[9]/span/span/div/img',
                '/html/body/div[2]/div[3]/div[3]/div[4]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[10]/span/span/div/img',
                '/html/body/div[2]/div[2]/div[7]/div[4]/div[3]/div/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[5]/span/span/div/img'
            ]

            for img_path in img_paths:
                try:
                    temp = web_driver.find_element(By.XPATH, img_path)
                    x = temp.get_attribute("src")
                    img_url.append(x)
                except Exception as e:
                    pass

        except Exception as e:
            img_path = '//*[@id="landingImage"]'
            temp = web_driver.find_element(By.XPATH, img_path)
            x = temp.get_attribute("src")
            img_url.append(x)
            continue

    img_url = list(set(img_url))

    for i in range(len(img_url)):
        pic = 'Pic' + str(i + 1)
        product_info[pic].append(img_url[i])

    if len(img_url) < 9:
        for i in range(9 - (9 - len(img_url)) + 1, 10, 1):
            pic = 'Pic' + str(i)
            product_info[pic].append('None')
    return product_info


def update_product_description(web_driver, product_info, index):
    text_folder = './product_description/'
    isExist = os.path.exists(text_folder)

    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(text_folder)
        print("The product_description folder was created!")

    web_driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    file_name = text_folder \
                + (product_info['URL'][index]).split('pd_rd_i=')[1][:9] \
                + ".txt"
    text_file = open(file_name, "a", encoding="utf-8")

    content = web_driver.page_source
    soup = BeautifulSoup(content)

    product_description = soup.find('div', {'id': 'productDescription'})
    for a in product_description.findAll('span'):
        text_file.write(a.text + '\n')
    text_file.close()
    product_info['Product description'].append(file_name)
    return product_info


if __name__ == '__main__':
    df = pd.DataFrame()
    product_info = init_product_info()
    count = 0

    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    link = "https://www.amazon.co.jp/-/en/gp/bestsellers/hpc/169976011/ref=zg_bs_pg_1?ie=UTF8&pg=1"
    driver.get(link)
    change_postcode(driver)
    scroll_until_the_end(driver)

    content = driver.page_source
    soup = BeautifulSoup(content)

    product_info = append_url(soup, product_info)
    for i in range(len(product_info['URL'])):
        print('Program is at product index', i)
        driver.get(product_info['URL'][i])

        content = driver.page_source
        soup = BeautifulSoup(content)

        product_info = update_price_and_title(soup, product_info)
        product_info = update_rating(soup, product_info)
        product_info = update_img(driver, product_info)
        product_info = update_product_description(driver, product_info, i)

        df2 = pd.DataFrame({'URL': [product_info['URL'][i]],
                            'Title': [product_info['Title'][i]],
                            'Price': product_info['Price'][i],
                            'Rating': product_info['Rating'][i],
                            'Pic1': product_info['Pic1'][i],
                            'Pic2': product_info['Pic2'][i],
                            'Pic3': product_info['Pic3'][i],
                            'Pic4': product_info['Pic4'][i],
                            'Pic5': product_info['Pic5'][i],
                            'Pic6': product_info['Pic6'][i],
                            'Pic7': product_info['Pic7'][i],
                            'Pic8': product_info['Pic8'][i],
                            'Pic9': product_info['Pic9'][i],
                            'Product description': product_info['Product description'][i]})
        df = df.append(df2, ignore_index=True)
        df.to_excel('output.xlsx')

    driver.quit()
    df.to_excel('output.xlsx')
