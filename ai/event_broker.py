class EventBroker:
    """Event broker for publishing and subscribing to events."""

    def __init__(self):
        self.topics = {}

    def publish(self, topic, **event):
        if topic in self.topics:
            for callback in self.topics[topic]:
                callback(event)

    def subscribe(self, topic, callback):
        if topic not in self.topics:
            self.topics[topic] = []

        self.topics[topic].append(callback)

    def unsubscribe(self, topic, callback):
        if topic in self.topics:
            self.topics[topic].remove(callback)

# Singleton instance
event_broker = EventBroker()
