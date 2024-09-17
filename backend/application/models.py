from application import db


class Event(db.Model):
    def __init__(self, title, description=None, date=None, lon=None, lat=None, image=None, link=None):
        self.title = title
        self.description = description
        self.date = date
        self.lon = lon
        self.lat = lat
        self.image = image
        self.link = link

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(500))
    date = db.Column(db.DateTime)
    lon = db.Column(db.Float)
    lat = db.Column(db.Float)
    image = db.Column(db.String(500))
    link = db.Column(db.String(500))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "date": self.date,
            "location": [self.lon, self.lat],
            "image": self.image,
            "link": self.link
        }


class Tag(db.Model):
    def __init__(self, name):
        self.name = name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class EventTags(db.Model):
    def __init__(self, event_id, tag_id):
        self.event_id = event_id
        self.tag_id = tag_id

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))