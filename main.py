import time
from pathlib import Path
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import config
import logging
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def read_input(path):
    """
    read input from input excel file
    """
    product_list = []
    sort_by = []
    brand = []
    try:
        # read each column into a list
        df = pd.read_excel(path)
        product_list = df['Product Type'].tolist()
        brand = df['Brand'].tolist()
        sort_by = df['Sort By'].tolist()
    except FileNotFoundError as f:
        logging.error("Input file not found")

    return product_list, sort_by, brand


def search(product_list, sort_list, brand_list):
    """
    search for specific product from prdouct_list;
    product_list_n:-type:list
    sort_by_n:-type:list
    brand_n:-type:list
    """
    try:

        for product in range(len(product_list)):
            time.sleep(2)
            search_field = browser.find_element_by_xpath(details_dict["search"])
            time.sleep(3)
            # clearing search_field and search for product
            search_field.clear()
            search_field.send_keys(product_list[product])
            time.sleep(3)
            search_go = browser.find_element_by_xpath(details_dict["go"]).click()
            time.sleep(3)
            # calling sort function for each product
            sort(sort_list[product], product,product_list, brand_list)
    except NoSuchElementException as n:
        logging.error("Exception is {}".format(n))
    except Exception as e:
        logging.error("Exception is:{}".format(e))


def sort(sort_item, index, product_list,brand_list_n):
    """ find sort element for the product passed
    """
    print(sort_item)
    time.sleep(15)
    # finding sort dropdown
    sort_value = wait(20, details_dict["sort"]).click()
    time.sleep(3)

    try:
        # find the dropdown option with the sort element and click
        drop_element = browser.find_element_by_xpath("//a[contains(text(),'" + sort_item + "')]")
        time.sleep(3)
        drop_element.click()
        time.sleep(7)
        # calling function to check the specific brand boxes
        brand_check(brand_list_n[index],product_list[index])
    except NoSuchElementException as n:
        logging.error("Element not found in sort function")
    except Exception as e:
        print("Sort function;Exception is {}".format(e))


def brand_check(brand_list_passed,product):
    """
    Search for the brand from input list after required modifications in the search bar
    :param brand_list_passed:
    :param product:
    :return:
    """
    time.sleep(5)
    try:
        see_more = browser.find_element_by_xpath(details_dict["see_more"])
        see_more.click()
    except NoSuchElementException as n:
        pass
    # split the brands by comma if more than one brand present to a new list
    new_brand = brand_list_passed.split(',')
    list_valid = []
    # iterate within the new list
    for brand_new in range(len(new_brand)):
        # remove spaces in between the product to make search easy
        new_brand[brand_new] = new_brand[brand_new].replace(" ", "")
        time.sleep(5)
        # construct xpath with the new brand iterations
        brand_element_xpath = "//li/span/a[contains(@href,'" + new_brand[brand_new] + "')]"
        try:
            time.sleep(5)
            brand_element = browser.find_element_by_xpath(brand_element_xpath)
            time.sleep(5)
            brand_element.click()
            time.sleep(5)
            list_valid.append(new_brand[brand_new])
        except NoSuchElementException as n:
            print("Exception is:{}".format(n))


    output_dictionary = choose_product(list_valid)
    write_excel(output_dictionary, product)
    # returning to all categories search
    time.sleep(5)
    wait(10, details_dict["all"]).click()
    time.sleep(25)
    all_cat = browser.find_element_by_xpath(details_dict["all_categories"]).click()
    time.sleep(5)


def choose_product(valid_brand):
    """
    Finding price, brand and review for the chosen product( should not be renewed and
    save it in a dictionary to be userd in output excel
    """
    count = 0
    product_name = []
    brand_name = []
    price = []
    review = []
    # find all product elements in the search page
    all_product_elements = browser.find_elements_by_xpath(details_dict["all_product_elements"])
    time.sleep(3)
    print(len(all_product_elements))
    # iterate over the search elements
    for search_index in range(len(all_product_elements)):
        time.sleep(5)
        # find product name
        prod_name = (all_product_elements[search_index].find_element_by_xpath(
            details_dict["product_name_search"])).text
        # check if product name has "Renewed" word in it.if yes skip;else find brand,review and rating
        if "Renewed" in prod_name:
            print("renewed")
            continue
        else:
            product_name.append(prod_name)
            brand_name.extend(valid_brand)
            try:
                print("inside try1")
                time.sleep(5)
                # find price of the product
                price_i = all_product_elements[search_index].find_element_by_xpath(
                    details_dict["price_search"]).get_attribute('innerHTML')
                price.append(price_i)
            except NoSuchElementException as n:
                print("inside except1")
                price.append("None")

                logging.error("Price element not found")

            try:
                time.sleep(10)
                print("inside try2")
                review_i = all_product_elements[search_index].find_element_by_xpath(
                    details_dict["review_search"]).get_attribute('innerHTML')
                review_i = review_i.replace(" stars", "")
                print(review_i)
                review.append(review_i)
            except NoSuchElementException as n:
                print("inside except2")
                review.append("None")
                logging.error("Review element not found")
            count = count + 1
            # only take 2 elements
            if (count == 2):
                break
    output_dictionary = {" product name": product_name, "brand": brand_name, "price": price, "review": review}

    return output_dictionary



def dict(product, brand, price, review):
    """
    make lists into dictionary
    """
    output_dictionary = {" product name": product, "brand": brand, "price": price, "review": review}

    return output_dictionary


def write_excel(dictionary, sheet):
    """
    write to an excel file as different sheets for different products
        """
    try:
        file_path = Path(details_dict["output_path"])
        df = pd.DataFrame(dictionary)
        # if file exists append the new sheet to avoid overwriting
        if file_path.exists():
            print("append")
            with pd.ExcelWriter(details_dict["output_path"], engine='openpyxl', mode='a') as writer:
                df.to_excel(writer, sheet_name=sheet, index=False)
        else:
            print("writing")
            df.to_excel(file_path, sheet_name=sheet, index=False)
    except Exception as e:
        logging.error("Exception is {}".format(e))


def wait(time_in_sec, element):
    """
    To implement explicit wait
    """
    waiti = WebDriverWait(browser, time_in_sec)
    element_wait = waiti.until(EC.presence_of_element_located((By.XPATH, element)))
    return element_wait


if __name__ == "__main__":
    # log file creation
    logging.basicConfig(filename="amazon.log", format='%(asctime)s %(message)s', filemode='w')
    details_dict = config.get_value()

    input_path = details_dict["input_path"]

    product_type_list, sort_list, brand_list = read_input(input_path)
    # load chrome driver
    browser = webdriver.Chrome(details_dict["chrome_driver"])

    browser.get(details_dict["amazon_path"])
    browser.maximize_window()
    # calling search function to search the product name from product_type_list
    search(product_type_list, sort_list, brand_list)
    browser.close()
