import csv
import json

import pandas as pd
import requests



data = pd.read_excel("../冠德111年至10月庫存-111.11.17.xlsx",
                     usecols="C, D, J,L,N")

print(data['冠德電器企業有限公司'])
print(type(data['冠德電器企業有限公司']))

print(type(data['冠德電器企業有限公司'][0]))

# print(type(data[4]))

print(type(data[4:10]))

class DataLoader:

    def __init__(self, file_name):
        self.list_target = []
        self.list_error = [('項次','型號', '種類', '總數', '單價','進貨時間')]
        self.data = pd.read_excel(file_name,
                     usecols="C, D, J,L,N")
        self.use_data = self.data[['冠德電器企業有限公司', 'Unnamed: 3', 'Unnamed: 9', 'Unnamed: 11']][4:]
        self.total_page = len(self.data) //50

    def make_dataset_loop(self):
        for p in range(1, self.total_page + 2):
            if p < (self.total_page + 1):
                for item in range((4 + 50 * (p - 1)), 44 + 50 * (p - 1)):
                    self.make_dataset(item)
            else:
                for item in range((4 + 50 * (p - 1)), len(data)):
                    self.make_dataset(item)

    def make_dataset(self,item):
        target = {}
        target['type_no'] = self.use_data['冠德電器企業有限公司'][item]
        target['kind'] = self.use_data['Unnamed: 3'][item]
        target['total'] = self.use_data['Unnamed: 9'][item]
        target['in_price'] = self.use_data['Unnamed: 11'][item]
        target['in_time'] = '2022-10-31'
        if target['type_no'] == target['kind'] or target['total'] < 0:
            tuple_tmp = (item, target['type_no'], target['kind'], target['total'], target['in_price'], target['in_time'])
            self.list_error.append(tuple_tmp)
        else:
            self.list_target.append(target)

    def send_data(self):
        headers = {
            'Content-Type': 'application/json'
        }
        for target in self.list_target:
            res = requests.post(url='http://127.0.0.1:8000/v1/products/out_database', headers=headers,
                                data=json.dumps(target))
            if res.status_code > 399:
                res_j = json.loads(res.text)
                print(res_j['data']['error'])

    def ouput_error(self):
        with open('error_data.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.list_error)

    def run(self):
        self.make_dataset_loop()
        self.send_data()
        self.ouput_error()
# df 可以透過 指定 欄位 去獲取該直欄的資料 只要在搭配index 就可以去所定該欄 特定位置的資料
# df_data = data[['冠德電器企業有限公司', 'Unnamed: 3', 'Unnamed: 9', 'Unnamed: 11']][4:]


if __name__ == '__main__':
    DL = DataLoader("../冠德111年至10月庫存-111.11.17.xlsx")
    DL.run()

