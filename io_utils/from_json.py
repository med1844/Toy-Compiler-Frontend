from abc import ABC, abstractmethod


class FromJson(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, obj):
        pass
