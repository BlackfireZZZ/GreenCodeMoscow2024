import requests
from bs4 import BeautifulSoup
from datetime import datetime
from geopy.geocoders import Nominatim
from application.models import Event
from application import db


def get_coordinates(place):
    geolocator = Nominatim(user_agent="event_parser")
    if location := geolocator.geocode(place):
        return location.longitude, location.latitude
    return None, None


def parse_page(query, page):
    url = f"https://www.mos.ru/search/afisha?no_spellcheck=0&page={page}&q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    events = []
    event_cards = soup.find_all('div', class_='css-p58yb7-Box')

    for card in event_cards:
        app.logger.info(card)
        title_tag = card.find('h5', class_='css-1apiv1r-Heading-Text')
        title = title_tag.text.strip() if title_tag else None

        description_tag = card.find('p', class_='css-vqppqt-Paragraph-Text')
        description = description_tag.text.strip() if description_tag else None

        date_tag = card.find('span', class_='css-1bffihw-Text')
        date_text = date_tag.text.strip() if date_tag else None
        date = None
        if date_text:
            try:
                date = datetime.strptime(date_text.split('·')[1].strip(), '%d %B %Y')
            except Exception:
                date = None

        link_tag = card.find('a', class_='css-1uvlm48-Link-Text')
        link = link_tag['href'] if link_tag else None

        image_tag = card.find('div', class_='sc-jOHGOj')
        image = image_tag['style'].split('url("')[1].split('")')[0] if image_tag else None

        # Получение координат места (если есть конкретное место в названии)
        lon, lat = None, None
        if title:
            lon, lat = get_coordinates(title)

        # Создаем объект события
        event = Event(title=title, description=description, date=date, lon=lon, lat=lat, image=image, link=link)
        events.append(event)

    return events


def parse_mosru_events():
    queries = ["Эко", "Экология"]
    all_events = []

    for query in queries:
        page = 1
        while True:
            events = parse_page(query, page)
            if not events:
                break
            all_events.extend(events)
            page += 1

    for event in all_events:
        db.session.add(event)

    db.session.commit()

