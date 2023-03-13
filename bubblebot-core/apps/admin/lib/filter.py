from typing import List


class CacheDataFilter:
    def __init__(self, cache_data: List[dict], filter_conditions: dict):
        self.cache_data = cache_data
        self.filter_conditions = filter_conditions

    def _get_resolve_conditions(slef, filter_conditions: dict):
        conditions: List[dict] = []
        for k, v in filter_conditions.items():
            filter = k.rsplit('__', 1)
            field = filter[0]
            if len(filter) == 2:
                condition = filter[1]
            else:
                condition = None
            value = v
            conditions.append({"field": field, "value": value, "condition": condition})
        return conditions

    def _get_filter(self, data: List[dict], conditions: list):
        if len(conditions) <= 0:
            return data
        tmp: dict = conditions.pop(0)
        field = tmp.get("field")
        value = tmp.get("value")
        excondition = tmp.get("condition")
        filtered_data = []
        for row in data:
            if field not in row:
                filtered_data.append(row)
            elif (not excondition) and (row.get(field) == value):
                filtered_data.append(row)
            elif (excondition == 'icontains') and (str(value).lower() in str(row.get(field)).lower()):
                filtered_data.append(row)
            elif (excondition == 'in') and (value in row.get(field)):
                filtered_data.append(row)

        return self._get_filter(filtered_data, conditions)

    def filter(self):
        resolve_conditions = self._get_resolve_conditions(self.filter_conditions)
        res = self._get_filter(self.cache_data, resolve_conditions)
        return res
