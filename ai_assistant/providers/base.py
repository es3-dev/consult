from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Strategy base: todos los proveedores exponen el mismo contrato."""

    name = "base"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
