from typing import Union
from django.db.models.query import QuerySet


class Pagination:
    def __init__(self, data: Union[QuerySet, list], page_index: int, per_page_num: int):
        self.data = data
        self.per_page_num = per_page_num
        self.query_index = page_index

        if isinstance(data, QuerySet):
            self.data_type = "queryset"
        elif isinstance(data, list):
            self.data_type = "list"
        else:
            raise ValueError("Invalid data type")

    @property
    def page_index(self):
        num = None
        if self.query_index > self.total_page_num:
            num = self.total_page_num
        elif self.query_index < 1:
            num = 1
        else:
            num = self.query_index
        return num

    @property
    def start_row_num(self) -> int:
        res = self.page_index * self.per_page_num - self.per_page_num
        return res

    @property
    def end_row_num(self) -> int:
        res = self.page_index * self.per_page_num
        return res

    @property
    def total_row_num(self) -> int:
        res = None
        if self.data_type == 'queryset':
            res = self.data.count()
        elif self.data_type == 'list':
            res = len(self.data)
        return res

    @property
    def total_page_num(self) -> int:
        res = None
        if self.total_row_num % self.per_page_num == 0:
            res = self.total_row_num // self.per_page_num
        else:
            res = self.total_row_num // self.per_page_num + 1
        if res < 1:
            res = 1
        return res

    @property
    def total_page_range(self) -> tuple:
        res = (1, self.total_page_num)
        return res

    @property
    def current_page_num(self) -> int:
        res = self.page_index
        return res

    @property
    def current_page_data_list(self):
        res = self.data[self.start_row_num : self.end_row_num]
        return res

    @property
    def current_row_range(self) -> tuple:
        res = (self.start_row_num + 1, self.start_row_num + len(self.current_page_data_list))
        return res

    @property
    def has_previous(self) -> bool:
        return True if self.current_page_num > 1 else False

    @property
    def has_next(self) -> bool:
        return True if self.current_page_num < self.total_page_num else False
