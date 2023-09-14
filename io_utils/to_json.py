from abc import ABC, abstractmethod


class ToJson(ABC):
    @abstractmethod
    def to_json(self):
        pass

