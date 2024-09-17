from application import *
from application.handle_event.events_routes import event_blueprint
from application.parcing.MosRu import parse_mosru_events

app.register_blueprint(event_blueprint, url_prefix='/event')

with app.app_context():
    db.create_all()

    #   parse_mosru_events()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
