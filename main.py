import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import csv
import pandas as pd

id = []
name = [] #name
size_list = []
product_lists  = []
product_images = [] #image links
items = []
product_price = [] # product each items
images_additional = [] # additonal image
product_description_add = [] #product description
pages_result = []
product_category = []

options = webdriver.ChromeOptions()
prefs = {"credentials_enable_service": False}
prefs = {"profile.password_manager_enabled": False}
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
ids = 1
page = 1
for i in range (1,5):
    driver.get(f'https://www.ebay.com/sch/i.html?_dmd=2&_dkr=1&iconV2Request=true&_ssn=sz-top1&store_name=sztop1&_oac=1&store_cat=0&_pgn={i}')

    driver.find_element(By.XPATH,"//button[@class='x-flyout__button']").click()
    driver.find_element(By.XPATH, "//span[@class='select']//select[@id='s0-50-12-5-4[1]-43-0-7-13-select']//option[@value='1']").click()
    driver.find_element(By.XPATH, "//input[@class='srp-shipping-location__form--inline btn btn--small btn--primary']").submit()
    get_url = driver.current_url
    page_source = driver.page_source

    soup = BeautifulSoup(page_source,features="lxml")

    pages = soup.find_all('a', {'class': 'pagination__item'})

    for page in pages:
        pages_result.append(page['href'])


    products = soup.find_all('div', {'class': 's-item__info clearfix'})

    for product in products:
        product_links = product.find('a', {'class': 's-item__link'})
        product_lists.append(product_links['href'])

    try:
        for product_list in product_lists[1:]:
            print(product_list)
            r = requests.get(product_list)
            soup = BeautifulSoup(r.text, 'lxml')
            image_links = soup.find_all('div',{'class':'v-pnl-item'})
            parent_title = soup.find('h1',{'class':'x-item-title__mainTitle'})
            title = parent_title.find('span',{'class':'ux-textspans ux-textspans--BOLD'}).text
            sizes =  soup.find_all('div', {'class': 'vi-msku-cntr'})
            div = soup.find(('nav',{'class': 'vi-bc-topM'}))
            category = div.find('div',{'class' : 'd-breadcrumb__wrapper'})

            #sizes = size.find('div', {'class':'u-flL sh-col'})

            parent_price = soup.find('div',{'class': 'mainPrice'})
            price = parent_price.find('span',{'class': 'notranslate'})
            final_price = float(price['content'])
            parent_size = soup.find('div', {'class':'u-flL  sh-col'})
            parent_description = soup.find('iframe')
            description_result = (parent_description['src'])
            #child_description = parent_description.find('div',{'class':'titlebar'})
            price_result = f"{final_price + (final_price * 0.30):.2f} "
            print(title)
            print(description_result)


            images = []

            for i in soup.select('div.v-pnl-item >img'):
                if i.get('src').replace('s-l64', 's-l2000') == '//p.ebaystatic.com/aw/pics/cmp/icn/iconImgNA_96x96.gif':
                    result = i.get('data-img-url').replace('s-l64', 's-l2000')
                    images.append(result)

                x = i.get('src').replace('s-l64', 's-l2000').replace(
                    '//p.ebaystatic.com/aw/pics/cmp/icn/iconImgNA_96x96.gif', "")
                images.append(x)
            list1 = filter(None, images)
            x = list(list1)

            r = requests.get(description_result)
            item_id = description_result.split('?')[1:].split('/')[-1]
            soup = BeautifulSoup(r.text, 'lxml')
            soup = BeautifulSoup(requests.get(description_result.format(item_id=item_id)).content, 'html.parser')
            final_description_result = soup.get_text(strip=True, separator='\n')
            print(final_description_result)
            """
            This will loop available of sizes and make as result in
            """

            if sizes:
                pass
            else:
                name.append(title)
                product_price.append(price_result)
                product_description_add.append(final_description_result)
                product_images.append(x[0])
                images_additional.append(",".join(x[1:]))
                size_list.append(" ")
                id.append(ids)
                product_category.append(category.text[12:])

            for size in sizes:
                decimal = 0
                l = size.find_all('option')
                for y in l[1:]:
                    if y.text[-14:] == '[out of stock]':
                        pass
                    else:
                        name.append(title)
                        product_price.append(price_result)
                        product_description_add.append(final_description_result)
                        product_images.append(x[0])
                        images_additional.append(",".join(x[1:]))
                        product_category.append(category.text[12:])
                        id.append(f'{ids}.{decimal}')
                        print(y.text)
                        size_list.append(y.text)

                        decimal += 1
                decimal = 0
            ids += 1
    except:
        pass


print(len(name))
print(len(product_description_add))
print(len(product_price))
print(len(product_images))
print(len(images_additional))
print(len((size_list)))
print(len(product_category))

products_scrape = pd.DataFrame({
    'id': id,
    'title': name,
    'item_group_id': name,
    'description': product_description_add,
    'price': product_price,
    'link': product_images,
    'image_link': product_images,
    'additional_image': images_additional,
    'size': size_list,
    'fb_product_category ': product_category,
    })

writer = pd.ExcelWriter('converted-to-excel.xlsx')
products_scrape.to_excel(writer)

writer.save()
