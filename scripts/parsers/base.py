from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ParseResult:
    title: str
    content: str
    parser_name: str
    success: bool = True
    error: str = ""


class ContentParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> ParseResult:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
