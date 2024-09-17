from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from application.models import Event
from application import db
from flask import Blueprint

from selenium.webdriver.common.by import By
from geopy.geocoders import Nominatim
import time
from datetime import datetime


event_blueprint = Blueprint('event', __name__)


@event_blueprint.route('/create', methods=['POST'])
def create_event(title, description, date, lon, lat, image):
    new_event = Event(title)
    if description:
        new_event.description = description
    if date:
        new_event.date = date
    if lon:
        new_event.lon = lon
    if lat:
        new_event.lat = lat
    if image:
        new_event.image = image
    db.session.add(new_event)
    db.session.commit()
    return new_event.to_dict()


# Функция для получения координат места
def get_coordinates(place):
    geolocator = Nominatim(user_agent="event_parser")
    location = geolocator.geocode(place)
    if location:
        return location.longitude, location.latitude
    return None, None


def init_driver():
    # Опции для Firefox
    options = Options()
    options.add_argument("--headless")  # Запуск без интерфейса
    options.add_argument("--disable-gpu")  # Отключить GPU (особенно для удаленных серверов)
    options.add_argument("--no-sandbox")  # Отключить sandbox (необязательно для Firefox)
    options.add_argument("--disable-dev-shm-usage")  # Для стабильной работы в контейнерах Docker
    options.add_argument("--disable-software-rasterizer")  # Отключение программного рендеринга
    options.add_argument("--start-maximized")  # Запуск в развернутом виде
    options.add_argument("--disable-infobars")  # Отключение информационных панелей
    options.add_argument("--disable-extensions")  # Отключение расширений

    # Создаем экземпляр сервиса для Firefox
    service = Service(executable_path="/usr/local/bin/geckodriver")  # Указываем путь к geckodriver

    # Возвращаем инстанс драйвера с указанными опциями и сервисом
    return webdriver.Firefox(service=service, options=options)


# Функция парсинга данных с одной страницы
def parse_page(driver, query, page):
    url = f"https://www.mos.ru/search/afisha?no_spellcheck=0&page={page}&q={query}"
    driver.get(url)
    time.sleep(3)  # Ждем, пока страница полностью загрузится

    events = []

    # Находим все карточки событий
    event_cards = driver.find_elements(By.CLASS_NAME, "css-p58yb7-Box")

    for card in event_cards:
        try:
            # Извлекаем название события
            title_element = card.find_element(By.TAG_NAME, "h5")
            title = title_element.text.strip()

            # Извлекаем описание события
            description_element = card.find_element(By.TAG_NAME, "p")
            description = description_element.text.strip()

            # Извлекаем дату события
            date_element = card.find_element(By.TAG_NAME, "span")
            date_text = date_element.text.split('·')[-1].strip()
            try:
                date = datetime.strptime(date_text, "%d %B %Y")
            except ValueError:
                date = None

            # Извлекаем ссылку на событие
            link_element = card.find_element(By.TAG_NAME, "a")
            link = link_element.get_attribute("href")

            # Извлекаем изображение
            image_element = card.find_element(By.CSS_SELECTOR, "div[style*='background-image']")
            image = image_element.value_of_css_property("background-image").split('url("')[1].split('")')[0]

            # Получаем координаты места события
            lon, lat = get_coordinates(title)

            # Создаем объект события
            event = Event(title=title, description=description, date=date, lon=lon, lat=lat, image=image, link=link)
            events.append(event)

        except Exception as e:
            print(f"Ошибка при парсинге события: {e}")
            continue

    return events


@event_blueprint.route('/parse', methods=['GET'])
def parse_mosru_events():
    driver = init_driver()
    queries = ["Эко", "Экология"]
    all_events = []

    for query in queries:
        page = 1
        while True:
            events = parse_page(driver, query, page)
            if not events:
                break  # Прерываем цикл, если на странице нет событий
            all_events.extend(events)
            page += 1  # Переходим на следующую страницу

    driver.quit()

    # Выводим все собранные события
    return [event.to_dict() for event in all_events]







