"""
Парсер плагина SPP

1/2 документ плагина
"""
import logging
import os
import time

import dateparser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.spp.types import SPP_document
from datetime import datetime
import pytz
from selenium.webdriver.chrome.webdriver import WebDriver
from random import uniform


class PaymentsDive:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'PaymentsDive'
    # HOST = "https://www.paymentsdive.com/"
    HOST = "https://www.paymentsdive.com/?page=2"
    _content_document: list[SPP_document]
    utc = pytz.UTC
    # date_begin = utc.localize(datetime(2023, 12, 6))

    def __init__(self, webdriver: WebDriver, last_document: SPP_document = None, max_count_documents: int = 100, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []
        self.driver = webdriver
        self.wait = WebDriverWait(self.driver, timeout=20)

        self.max_count_documents = max_count_documents
        self.last_document = last_document

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        try:
            self._parse()
        except Exception as e:
            self.logger.debug(f'Parsing stopped with error: {e}')
        else:
            self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -

        self.driver.get(self.HOST)  # Открыть страницу с материалами
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dash-feed')))

        # Окно с куками пропадает самостоятельно через 2-3 секунды
        # try:
        #    cookies_btn = self.driver.find_element(By.CLASS_NAME, 'ui-button').find_element(By.XPATH,
        #                                                                                    '//*[text() = \'Accept\']')
        #    self.driver.execute_script('arguments[0].click()', cookies_btn)
        #    self.logger.info('Cookies убран')
        # except:
        #    self.logger.exception('Не найден cookies')
        #    pass

        # self.logger.info('Прекращен поиск Cookies')
        time.sleep(3)

        while True:

            # self.logger.debug('Загрузка списка элементов...')

            doc_table = self.driver.find_element(By.CLASS_NAME, 'dash-feed').find_elements(By.XPATH,
                                                                                           '//*[contains(@class,\'row feed__item\')]')
            # self.logger.debug('Обработка списка элементов...')

            # Цикл по всем строкам таблицы элементов на текущей странице
            # self.logger.info(f'len(doc_table) = {len(doc_table)}')
            # print(doc_table)
            # for element in doc_table:
            #     print(element.text)
            #     print('*'*45)

            for i, element in enumerate(doc_table):
                # continue
                # print(i)
                # print(element)
                # print(doc_table[i])
                if 'feed-item-ad' in doc_table[i].get_attribute('class'):
                    # print(doc_table[i].get_attribute('class'))
                    # print(doc_table[i].text)
                    continue

                element_locked = False

                try:
                    title = doc_table[i].find_element(By.XPATH, './/*[contains(@class,\'feed__title\')]').text
                    # print(title)
                    # title = element.find_element(By.XPATH, '//*[@id="feed-item-title-1"]/a').text

                except:
                    # self.logger.exception('Не удалось извлечь title')
                    title = ' '

                # try:
                #     other_data = element.find_element(By.CLASS_NAME, "secondary-label").text
                # except:
                #     self.logger.exception('Не удалось извлечь other_data')
                #     other_data = ''
                # // *[ @ id = "main-content"] / ul / li[1] / div[2] / span[2]
                # // *[ @ id = "main-content"] / ul / li[2] / div[2] / span[2]
                other_data = None

                # try:
                #    date = dateparser.parse(date_text)
                # except:
                #    self.logger.exception('Не удалось извлечь date')
                #    date = None

                try:
                    abstract = doc_table[i].find_element(By.CLASS_NAME, 'feed__description').text
                except:
                    # self.logger.exception('Не удалось извлечь abstract')
                    abstract = None

                book = ' '

                try:
                    web_link = doc_table[i].find_element(By.XPATH, './/*[contains(@class,\'feed__title\')]').find_element(
                        By.TAG_NAME, 'a').get_attribute('href')
                except:
                    # self.logger.exception('Не удалось извлечь web_link, пропущен')
                    web_link = None
                    continue
                    # web_link = None

                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get(web_link)
                time.sleep(5)
                # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.print-wrapper')))

                try:
                    pub_date = self.utc.localize(
                        dateparser.parse(' '.join(self.driver.find_element(By.CLASS_NAME, 'published-info').text.split()[1:])))
                except:
                    # self.logger.exception('Не удалось извлечь pub_date')
                    pub_date = None

                try:
                    text_content = self.driver.find_element(By.XPATH, '//div[contains(@class, \'large medium article-body\')]').text
                except:
                    # self.logger.exception('Не удалось извлечь text_content')
                    text_content = None

                doc = SPP_document(None,
                                   title,
                                   abstract,
                                   text_content,
                                   web_link,
                                   None,
                                   other_data,
                                   pub_date,
                                   datetime.now())

                self.find_document(doc)

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            try:
                pagination_arrow = self.driver.find_element(By.XPATH, '//div[contains(@class,\'pagination\')]/a[2]')
                pg_num = pagination_arrow.get_attribute('href')
                self.driver.execute_script('arguments[0].click()', pagination_arrow)
                time.sleep(3)
                # self.logger.info(f'Выполнен переход на след. страницу: {pg_num}')
                print('=' * 90)

                # if int(pg_num[-1]) > 5:
                #     # self.logger.info('Выполнен переход на 6-ую страницу. Принудительное завершение парсинга.')
                #     break

            except:
                # self.logger.exception('Не удалось найти переход на след. страницу. Прерывание цикла обработки')
                break

        # ---
        # ========================================
        ...

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    def find_document(self, _doc: SPP_document):
        """
        Метод для обработки найденного документа источника
        """
        if self.last_document and self.last_document.hash == _doc.hash:
            raise Exception(f"Find already existing document ({self.last_document})")

        if self.max_count_documents and len(self._content_document) >= self.max_count_documents:
            raise Exception(f"Max count articles reached ({self.max_count_documents})")

        self._content_document.append(_doc)
        self.logger.info(self._find_document_text_for_logger(_doc))