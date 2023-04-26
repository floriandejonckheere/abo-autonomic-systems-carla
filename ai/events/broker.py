class Broker:
    """Event broker for publishing and subscribing to events."""

    def __init__(self):
        self.topics = {}

    def publish(self, topic, message):
        if topic in self.topics:
            for callback in self.topics[topic]:
                callback(message)

    def subscribe(self, topic, callback):
        if topic not in self.topics:
            self.topics[topic] = []

        self.topics[topic].append(callback)

    def unsubscribe(self, topic, callback):
        if topic in self.topics:
            self.topics[topic].remove(callback)

# Broker singleton
broker = Broker()
