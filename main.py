import os
import re
import warnings
from pprint import pprint

import requests
import urllib3
from bs4 import BeautifulSoup


def export_to_tsv(data: list, filepath: str, encoding='utf-8'):
    with open(filepath, mode='w', encoding=encoding) as outfile:
        for row in data:
            row_text = '\t'.join(row)
            outfile.write(row_text)
            outfile.write('\n')


def main():
    wikipedia_url = 'https://en.wikipedia.org/wiki/List_of_j%C5%8Dy%C5%8D_kanji'
    page = requests.get(wikipedia_url)

    if page.ok:
        soup = BeautifulSoup(page.content)
        table_classname = 'wikitable'
        kanji_table = soup.find(class_=table_classname)
        if kanji_table is None:
            raise Exception(f'The wikipedia page format has been changed!')

        # reference https://stackoverflow.com/a/23377804/8364403
        table_data = []
        table_body = kanji_table.find('tbody')
        rows = table_body.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            # extract the text
            row_data = [e.text.strip() for e in cols]
            if len(row_data) < 2:
                warnings.warn(f'{row_data} does not have enough data!')
                continue

            # extract kanji number and the kanji itself
            kanji_number = row_data[0]
            if not re.match(r'\d+', kanji_number):
                # the first row does not contain only number characters.
                warnings.warn(f'{row_data} has non-number character(s) in the first column!')  # noqa
                continue
            # kanji_number is still in string format

            kanji = row_data[1]
            if len(kanji) < 1:
                # the kanji text is probably empty.
                warnings.warn(f'{row_data} does not have a kanji in the second column!')  # noqa
            else:
                # remove reference annotation added by wikipedia
                # only the the first character and skip trailling annotation
                kanji = kanji[:1]

            kanji_data = (kanji_number, kanji)
            table_data.append(kanji_data)

        # pprint(table_data)
        # print(len(table_data))
        export_to_tsv(table_data, 'jouyou_kanji_list.tsv')
    else:
        print(page.status_code)
        raise Exception(f'The server responses with status code {page.status_code}!')  # noqa


if __name__ == '__main__':
    main()
