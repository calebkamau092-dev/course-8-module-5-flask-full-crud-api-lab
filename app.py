from flask import Flask, jsonify, request

app = Flask(__name__)


class Event:
    def __init__(self, id, title):
        self.id = id
        self.title = title

    def to_dict(self):
        return {"id": self.id, "title": self.title}


# In-memory "database"
events = [
    Event(1, "Tech Meetup"),
    Event(2, "Python Workshop")
]


def find_event(event_id):
    """Return the event with this id, or None if it doesn't exist."""
    return next((event for event in events if event.id == event_id), None)


def get_title(data):
    """Return a cleaned-up title from the JSON body, or None if it's missing or blank."""
    if not isinstance(data, dict):
        return None
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    return title.strip()


@app.route("/", methods=["GET"])
def welcome():
    return jsonify({"message": "Welcome to the Events API"}), 200


@app.route("/events", methods=["GET"])
def get_events():
    return jsonify([event.to_dict() for event in events]), 200


# Create a new event from JSON input
@app.route("/events", methods=["POST"])
def create_event():
    title = get_title(request.get_json(silent=True))
    if title is None:
        return jsonify({"error": "Title is required"}), 400

    # Next id is one more than the highest existing id, so ids are never reused.
    new_id = max((event.id for event in events), default=0) + 1
    event = Event(new_id, title)
    events.append(event)
    return jsonify(event.to_dict()), 201


# Update the title of an existing event
@app.route("/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": "Event not found"}), 404

    title = get_title(request.get_json(silent=True))
    if title is None:
        return jsonify({"error": "Title is required"}), 400

    event.title = title
    return jsonify(event.to_dict()), 200


# Remove an event from the list
@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": "Event not found"}), 404

    events.remove(event)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)