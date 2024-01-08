import time

from lxml import html
from selenium.webdriver.common.by import By
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

from SeleniumHelper import SeleniumHelper


class RoomSearch:
    BOOK_ROOM_ID = 'btn-main-book-a-room-pink'
    SELECT_PROPERTY_DROPDOWN_XPATH = '//select[@id="BookingAvailabilityForm_Residence"]'
    SELECT_PROPERTY_DATE_DROPDOWN_XPATH = '//select[@id="BookingAvailabilityForm_BookingPeriod"]'
    ROOM_TYPE_FILTER_XPATH = '//input[@value="Ensuite"]'
    ROOM_TIER_COLLAPSE_BTN_XPATH = '//button[@data-toggle="collapse"]/strong[contains(text(),"ROOM TIER")]'
    ROOM_TIER_XPATH = '//input[@value="Bronze"]'
    QUICK_VIEW_XPATH = '//button[@class="btn quick-view"]/span'
    CLOSE_BUTTON_XPATH = '//button[@aria-label="Close" and @data-dismiss="modal"]'
    APPLY_BUTTON_XPATH = '//div[@class="sp-content"]/div//a/span[contains(text(),"Apply")]'
    EMAIL_XPATH = '//input[@id="login_username"]'
    PASS_XPATH = '//input[@id="login_password"]'
    LOGIN_BUTTON_XPATH = '//button[@id="oa_login_submit"]'
    RETURN_TO_APPLICATION_XPATH = '//a[@data-load-msg="load"]'

    def __init__(self, helper):
        self.helper = helper
        self.room_details = []
        self.username = 'unmeshabhowmik@gmail.com'
        self.password = 'unmesha@26'
        self.quick_view_details = {}
        self.final_details = {}
        self.all_rooms = []
        # Set up MongoDB connection

    def start_scraper(self):
        try:
            self.open_and_book_rooms()
            self.select_drop_downs()
            self.apply_room_filters()
            self.capture_details_from_quick_view()
            self.login()
            self.capture_room_details()
            self.push_to_mongo()
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        finally:
            self.helper.close_browser()

    def open_and_book_rooms(self):
        self.helper.open_url("https://www.chapter-living.com")
        self.go_to_book_rooms_page()
        self.helper.wait_for_page_load('//h2[@class="text-uppercase"]/strong')
        print("Redirection successful!")

    def go_to_book_rooms_page(self):
        try:
            self.helper.click_element(By.ID, self.BOOK_ROOM_ID)
            self.helper.wait_for_page_load('//h2[@class="text-uppercase"]/strong')
            print("Redirection successful!")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def select_drop_downs(self):
        self.helper.scroll_to_element(By.XPATH, self.SELECT_PROPERTY_DROPDOWN_XPATH)
        self.helper.wait_for_page_to_stop_loading()
        self.helper.select_dropdown_value(By.XPATH, 'BookingAvailabilityForm_Residence', 'CHAPTER KINGS CROSS')
        self.helper.wait_for_page_to_stop_loading()
        self.helper.click_element(By.XPATH, self.SELECT_PROPERTY_DATE_DROPDOWN_XPATH)
        self.helper.select_dropdown_value(By.XPATH, 'BookingAvailabilityForm_BookingPeriod',
                                          'SEP 24 - AUG 25 (51 WEEKS)')
        self.helper.wait_for_page_to_stop_loading()

    def apply_room_filters(self):
        self.helper.scroll_to_element(By.XPATH, self.ROOM_TYPE_FILTER_XPATH)
        self.helper.wait_until_clickable_and_click(By.XPATH, self.ROOM_TYPE_FILTER_XPATH)
        print('Clicked on ensuite')
        # self.helper.scroll_to_element(By.XPATH, self.ROOM_TIER_COLLAPSE_BTN_XPATH)
        self.helper.wait_until_clickable_and_click(By.XPATH, self.ROOM_TIER_COLLAPSE_BTN_XPATH)
        print('Clicked on arrow')
        self.helper.wait_for_page_load(self.ROOM_TIER_XPATH)
        try:
            self.helper.wait_until_clickable_and_click(By.XPATH, self.ROOM_TIER_XPATH)
        except:
            try:
                self.helper.click_element(By.XPATH, self.ROOM_TIER_COLLAPSE_BTN_XPATH)
                self.helper.click_element(By.XPATH, self.ROOM_TIER_XPATH)
            except Exception as e:
                print(e)
        print('Clicked on bronze')

    def capture_details_from_quick_view(self):
        self.helper.wait_for_page_to_stop_loading()
        print('aa')
        self.helper.wait_until_clickable_and_click(By.XPATH, self.QUICK_VIEW_XPATH)
        page_source = self.helper.get_page_source()
        tree = html.fromstring(page_source)
        self.quick_view_details = {
            "quick_view_appartment_name": self.helper.clean_text(
                tree.xpath('//p[@id="apartmentModal-name"]')[0].text_content()),
            "quick_view_appartment_type": self.helper.clean_text(
                tree.xpath('//p[@id="apartmentModal-room"]/strong')[0].text_content()),
            "quick_view_appartment_price": self.helper.clean_text(
                tree.xpath('//p[@id="apartmentModal-price"]')[0].text_content()),
            "quick_view_appartment_description": self.helper.clean_text(
                tree.xpath('//div[@id="apartmentModal-description"]')[0].text_content()),
            "quick_view_appartment_features": self.helper.clean_text(
                tree.xpath('//ul[@id="apartmentModal-features"]')[0].text_content())
        }

    def login(self):
        time.sleep(3)
        self.helper.click_element(By.XPATH, self.CLOSE_BUTTON_XPATH)
        time.sleep(7)
        self.helper.wait_for_page_to_stop_loading()
        self.helper.click_element(By.XPATH, self.APPLY_BUTTON_XPATH)
        self.helper.wait_for_page_to_stop_loading()
        self.helper.input_text(By.XPATH, self.EMAIL_XPATH, self.username)
        self.helper.input_text(By.XPATH, self.PASS_XPATH, self.password)
        self.helper.wait_for_page_to_stop_loading()
        self.helper.click_element(By.XPATH, self.LOGIN_BUTTON_XPATH)
        self.helper.wait_for_page_to_stop_loading()
        time.sleep(5)
        try:
            self.helper.click_element(By.XPATH, self.RETURN_TO_APPLICATION_XPATH)
        except Exception as e:
            print(e)
        time.sleep(5)

    def capture_room_details(self):
        self.helper.scroll_to_end()
        page_source = self.helper.get_page_source()
        tree = html.fromstring(page_source)
        parent_xpath = tree.xpath('//div[@class="sus-unit-space-details"]')
        for sub_ele in parent_xpath:
            details = {
                'building': self.helper.clean_text(
                    sub_ele.xpath('.//dt[text()="Building"]/following-sibling::dd[@class="value"]/text()')[0].strip()),
                'rent': self.helper.clean_text(
                    sub_ele.xpath('.//dt[text()="Rent"]/following-sibling::dd[@class="value"]/text()')[0].strip()),
                'deposit': self.helper.clean_text(
                    sub_ele.xpath('.//dt[text()="Deposit"]/following-sibling::dd[@class="value"]/text()')[0].strip()),
                'amenities': self.helper.clean_text(
                    sub_ele.xpath('.//dt[text()="Amenities"]/following-sibling::dd[@class="value"]/text()')[0].strip()),
                'unit_spaces': [],
            }

            unit_space_rows = sub_ele.xpath('.//table[@class="unit-space-table"]//tr[@class=""]')
            for row in unit_space_rows:
                space = self.helper.clean_text(row.xpath('./td[2]/text()')[0].strip())
                status = self.helper.clean_text(row.xpath('./td[3]/text()')[0].strip())
                details['unit_spaces'].append({'space': space, 'status': status})

            payment_options = sub_ele.xpath('.//ul[@class="radio-group-list"]/li[@class="radio-group-item"]')
            details['payment_options'] = [{'plan_id': self.helper.clean_text(option.xpath('./input/@value')[0]),
                                           'plan_name': self.helper.clean_text(
                                               option.xpath('./span[@class="value"]/text()')[0].strip())}
                                          for option in payment_options]

            self.final_details = {**details, **self.quick_view_details}
            self.all_rooms.append(self.final_details)

        print(self.all_rooms)

    def push_to_mongo(self):
        escaped_username = quote_plus("Chapterliving")
        escaped_password = quote_plus("Unmesha@26")

        uri = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.w8bb2ld.mongodb.net/?retryWrites=true&w=majority"

        client = MongoClient(uri, server_api=ServerApi('1'))

        db = client['Chapterliving']
        collection = db['room_details']
        result = collection.insert_many(self.all_rooms)

        # Print the inserted document IDs
        print("Inserted document IDs:", result.inserted_ids)

        # Close the MongoDB connection
        client.close()


helper = SeleniumHelper()
room_search = RoomSearch(helper)
room_search.start_scraper()
