import datetime
import json
import os

import requests
import xmltodict

from excepions import CalcBaseException, CalcSymException, CalcAmountException


class APICurses:

    def __init__(self):
        self.url = 'https://www.cbr.ru/scripts/XML_daily.asp'
        self.json_file = 'currency.json'

    @property
    def cbr_req(self):
        # Выясняем запрашивали ли мы сегодня курс, если нет - запрашиваем
        # "свежий" курс и сохраняем его в json файл. Дальше работаем с ним
        # Тем самым сокращаем запросы на сервер до одного в день

        t = os.path.getmtime(self.json_file)
        file_date = datetime.date.fromtimestamp(t)

        if any([
            datetime.date.today() > file_date,
            not os.stat(self.json_file).st_size
        ]):
            cbr_currency = xmltodict.parse(requests.get(self.url).text)
            with open(self.json_file, 'w') as js_file:
                json.dump(cbr_currency, js_file)

        # "Вытаскиваем" информацию из файла и создаем удобный для нас словарь
        curses = {}
        key = val = None
        with open(self.json_file, 'r') as js_file:
            cbr_currency = json.load(js_file)
        for val_dict in cbr_currency['ValCurs']['Valute']:
            for _ in val_dict:
                key = val_dict['CharCode']
                val = float(val_dict['Value'].replace(',', '.')), \
                    int(val_dict['Nominal']), val_dict['Name']
            curses[key] = val
        return curses

    @property
    def cur_list(self):
        # Создание списка команд (они же доступные валюты)
        val_list = []
        for key in self.cbr_req:
            val_list.append(key.lower())
        return val_list

    def currency(self, val):
        # Курс запрошенной валюты
        val = val.replace('/', '').upper()
        message = f'Курс: {self.cbr_req[val][1]} ' \
                  f'{self.cbr_req[val][2]} = ' \
                  f'{self.cbr_req[val][0]} руб.'
        return message

    @property
    def all_currency(self):
        # Выводим все доступные валюты с их текущим курсом
        all_curses = self.cbr_req
        message_all = 'Курс всех доступных валют:\n\n'
        for key_all in all_curses:
            message_all += f'/{key_all.lower()} : {all_curses[key_all][1]} ' \
                           f'{all_curses[key_all][2]} = ' \
                           f'{all_curses[key_all][0]} руб.\n\n'
        return message_all


class Calculate:

    @staticmethod
    def convert(curses, base, sym, amount):

        # Проверим корректность введенных данных
        if any([not isinstance(base, str), len(base) != 3]):
            return CalcBaseException()

        if any([not isinstance(sym, str), len(sym) != 3]):
            return CalcSymException()

        try:
            amount = float(amount.replace(',', '.'))
        except ValueError:
            return CalcAmountException()

        base = base.upper()
        try:
            base_cost = 1 if base == 'RUB' else \
                curses[base][0] / curses[base][1]
        except KeyError:
            return CalcBaseException()

        sym = sym.upper()
        try:
            sym_cost = 1 if sym == 'RUB' else \
                curses[sym][0] / curses[sym][1]
        except KeyError:
            return CalcSymException

        # Рассчитываем стоимость валюты
        price = round(base_cost / sym_cost * amount, 4)
        price_message = f'Стоимость {amount} {base} = {price} {sym}'

        # Если валюты для конвертации одинаковы - показываем, что они равны
        # Но добавляем к сообщению Facepalm
        if base == sym:
            price_message += '  \U0001F926'

        return price_message
