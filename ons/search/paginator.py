"""
Paginator class - replicates pagination functionality from babbage
"""
import math

from config import SEARCH_CONFIG


class Paginator(object):

    def __init__(
            self,
            number_of_results: int,
            current_page: int,
            result_per_page: int = SEARCH_CONFIG.results_per_page,
            max_visible_links: int = SEARCH_CONFIG.max_visible_paginator_link):

        self.current_page = current_page
        self.number_of_pages = Paginator.calculate_number_of_pages(
            number_of_results, result_per_page)
        self.end = Paginator.calculate_end(
            self.number_of_pages, current_page, max_visible_links)
        self.start = Paginator.calculate_start(
            self.number_of_pages, max_visible_links, self.end)
        self.pages = self.get_page_list()
        self.size = int(result_per_page)

        self._json = {
            "numberOfPages": self.number_of_pages,
            "currentPage": self.current_page,
            "start": self.start,
            "end": self.end,
            "pages": self.pages
        }

    @staticmethod
    def calculate_end(
            number_of_pages: int,
            current_page: int,
            max_visible: int) -> int:
        """
        Calculates the last page number that should be shown at the bottom of the SERP
        :param number_of_pages:
        :param current_page:
        :param max_visible:
        :return:
        """
        max_pages = number_of_pages
        if max_pages < max_visible:
            return int(max_pages)

        # Half of the pages are visible after current page
        end = float(current_page) + math.ceil(float(max_visible) / 2.0)

        end = max_pages if end > max_pages else end
        end = max_visible if end < max_visible else end
        return int(end)

    @staticmethod
    def calculate_start(
            number_of_pages: int,
            max_visible: int,
            end: int) -> int:
        """
        Calculates the first page number that should be shown at the bottom of the SERP
        :param number_of_pages:
        :param max_visible:
        :param end:
        :return:
        """
        if number_of_pages <= max_visible:
            return 1
        start = float(end) - float(max_visible) + 1
        return int(max(start, 1))

    @staticmethod
    def calculate_number_of_pages(
            number_of_results: int,
            results_per_page: int) -> int:
        """
        Calculates the total number of available pages for a given SERP size
        :param number_of_results:
        :param results_per_page:
        :return:
        """
        return int(
            math.ceil(
                float(number_of_results) /
                max(float(results_per_page), 1)))

    def get_page_list(self) -> list:
        """
        Returns a list of page numbers to be shown at the bottom of the SERP
        :return:
        """
        page_list = [p for p in range(self.start, self.end + 1)]
        return page_list

    def to_dict(self) -> dict:
        """
        Return a JSON representation of the paginator
        :return:
        """
        return self.__json__()

    def __json__(self) -> dict:
        """
        Return a JSON representation of the paginator
        :return:
        """
        return self._json
