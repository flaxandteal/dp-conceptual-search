import abc
from typing import List

from supervised_models.src.page import Page


class DocumentReader(abc.ABC):

    @abc.abstractmethod
    def load_pages(self) -> List[Page]:
        pass
