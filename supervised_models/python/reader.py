import abc
from typing import List

from supervised_models.python.page import Page


class DocumentReader(abc.ABC):

    @abc.abstractmethod
    def load_pages(self) -> List[Page]:
        pass
