class BotUserException(Exception):
    pass


class CalcException(Exception):
    pass


class CalcBaseException(CalcException):
    def __str__(self):
        return 'Первый параметр задан некорректно!\n/help'


class CalcSymException:
    def __str__(self):
        return 'Второй параметр задан некорректно!\n/help'


class CalcAmountException:
    def __str__(self):
        return 'Третий параметр некорректен!\n/help'
