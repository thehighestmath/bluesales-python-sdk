# -*- coding: utf-8 -*-


class HttpError(Exception):
    pass


class WrongLoginOrPassword(Exception):
    pass


class TooLargeBoarders(Exception):
    pass


class BlueSalesError(Exception):
    pass
