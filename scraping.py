import requests
from bs4 import BeautifulSoup
import time
import csv
import numpy as np
import urllib.parse
import os
from retry import retry


# 参考記事
# https://qiita.com/shota_seki/items/0481bb202ac10a984d72
# https://qiita.com/tomyu/items/a08d3180b7cbe63667c9

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_filepath = os.path.join(script_dir, 'scraped_data.csv')

data_samples = []
max_page = 2000

# SUUMOを東京都23区のみ指定して検索して出力した画面のurl(ページ数フォーマットが必要)
url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13101&sc=13102&sc=13103&sc=13104&sc=13105&sc=13113&sc=13106&sc=13107&sc=13108&sc=13118&sc=13121&sc=13122&sc=13123&sc=13109&sc=13110&sc=13111&sc=13112&sc=13114&sc=13115&sc=13120&sc=13116&sc=13117&sc=13119&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=25&pc=50&page={}'

# リクエストがうまく行かないパターンを回避するためのやり直し
@retry(tries=3, delay=10, backoff=2)
def load_page(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup

start_time = time.time()
times = []

for page in range(1, max_page + 1):
    page_start_time = time.time()
    soup = load_page(url.format(page))
    properties = soup.find_all(class_='cassetteitem')

    for property in properties:

        # 建物情報
        data_home = []
        # カテゴリ
        data_home.append(property.find(class_='ui-pct ui-pct--util1').text.strip())
        # 建物名
        data_home.append(property.find(class_='cassetteitem_content-title').text.strip())
        # 住所
        data_home.append(property.find(class_='cassetteitem_detail-col1').text.strip())
        # 最寄り駅のアクセス
        property_col2 = property.find(class_='cassetteitem_detail-col2')
        for property_col2_detail in property_col2.find_all(class_='cassetteitem_detail-text'):
            data_home.append(property_col2_detail.text.strip())
        # 築年数と階数
        property_col3 = property.find(class_='cassetteitem_detail-col3')
        for property_col3_detail in property_col3.find_all('div'):
            data_home.append(property_col3_detail.text.strip())

        # 部屋情報
        rooms = property.find(class_='cassetteitem_other')
        for room in rooms.find_all(class_='js-cassette_link'):
            data_room = []

            # 部屋情報が入っている表を探索
            for id_, room_detail in enumerate(room.find_all('td')):
                # 階
                if id_ == 2:
                    data_room.append(room_detail.text.strip())
                # 家賃と管理費
                elif id_ == 3:
                    data_room.append(room_detail.find(class_='cassetteitem_other-emphasis ui-text--bold').text.strip())
                    data_room.append(room_detail.find(class_='cassetteitem_price cassetteitem_price--administration').text.strip())
                # 敷金と礼金
                elif id_ == 4:
                    data_room.append(room_detail.find(class_='cassetteitem_price cassetteitem_price--deposit').text.strip())
                    data_room.append(room_detail.find(class_='cassetteitem_price cassetteitem_price--gratuity').text.strip())
                # 間取りと面積
                elif id_ == 5:
                    data_room.append(room_detail.find(class_='cassetteitem_madori').text.strip())
                    data_room.append(room_detail.find(class_='cassetteitem_menseki').text.strip())
                # URL
                elif id_ == 8:
                    get_url = room_detail.find(class_='js-cassette_link_href cassetteitem_other-linktext').get('href')
                    abs_url = urllib.parse.urljoin(url, get_url)
                    data_room.append(abs_url)

            # 物件情報と部屋情報をくっつける
            data_sample = data_home + data_room
            data_samples.append(data_sample)

    # 負荷をかけないように1アクセスごとに1秒休む
    time.sleep(1)

    # 進捗確認のための表示
    page_finish_time = time.time()
    page_time = page_finish_time - page_start_time
    times.append(page_time)
    print(f'{page}ページ目：{page_time}秒')
    print(f'総取得件数：{len(data_samples)}')
    print(f'完了：{round(page / max_page * 100, 3)}%')
    estimated_time = np.mean(times) * (max_page - page)
    hour = int(estimated_time / 3600)
    minute = int((estimated_time % 3600) / 60)
    second = int(estimated_time % 60)
    print(f'残り時間：{hour}時間{minute}分{second}秒\n')

with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['カテゴリ', '建物名', '住所', '最寄り駅1', '最寄り駅2', '最寄り駅3', '築年数', '階数', '階', '家賃', '管理費', '敷金', '礼金', '間取り', '面積', 'URL'])
    writer.writerows(data_samples)

finish_time = time.time()
print('総経過時間：', finish_time - start_time)