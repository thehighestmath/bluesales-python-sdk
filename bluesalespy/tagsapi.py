# -*- coding: utf-8 -*-
from bluesalespy.methods import TagsMethods
from bluesalespy.request import RequestApi


class TagsAPI:
    def __init__(self, request_api: RequestApi) -> None:
        self.request_api = request_api

    def add(self, name: str, add_to_beginning: bool = False) -> dict:
        """Добавить тег.

        Args:
            name: название тега.
            add_to_beginning: если ``True``, тег добавляется в начало списка.

        Returns:
            Созданный тег.

        Example::

            bs.tags.add('VIP', add_to_beginning=True)
        """
        data = {
            "name": name,
            "addToBeginning": add_to_beginning,
        }
        return self.request_api.send(TagsMethods.add, data=data)
