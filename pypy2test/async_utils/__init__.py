import json
from twisted.internet.task import cooperate


class AsyncJSON(object):
    def __init__(self, value, cooperator=None):
        self._value = value
        self._consumer = None
        self._iterable = None
        self._task = None
        self.cooperate = cooperator.cooperate if cooperator else cooperate

    def begin_producing(self, consumer):
        self._consumer = consumer
        self._iterable = json.JSONEncoder().iterencode(self._value)
        self._consumer.registerProducer(self, True)
        self._task = self.cooperate(self._produce())
        d = self._task.whenDone()
        d.addBoth(self._unregister)
        return d

    def pause_producing(self):
        self._task.pause()

    def resume_producing(self):
        self._task.resume()

    def stop_producing(self):
        self._task.stop()

    def beginProducing(self, consumer):
        return self.begin_producing()

    def pauseProducing(self):
        return self.pause_producing()

    def resumeProducing(self):
        return self.resume_producing()

    def stopProducing(self):
        return self.stop_producing()

    def _produce(self):
        for chunk in self._iterable:
            self._consumer.write(chunk)
            yield None

    def _unregister(self, pass_through):
        self._consumer.unregisterProducer()
        return pass_through
