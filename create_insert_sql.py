import csv
import os
import re


def generate_insert_statements():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    csv_file_path = os.path.join(current_directory, "scraped_data.csv")
    rental_properties_file = os.path.join(current_directory, "insert_rental_properties.sql")
    nearest_stations_file = os.path.join(current_directory, "insert_nearest_stations.sql")

    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile, \
         open(rental_properties_file, mode='w', encoding='utf-8') as rental_sqlfile, \
         open(nearest_stations_file, mode='w', encoding='utf-8') as station_sqlfile:
        
        reader = csv.DictReader(csvfile)
        
        station_insert_template = """
        INSERT INTO nearest_stations (
            rental_property_id, route_name, station_name, transport_mode, time_required
        ) VALUES ({}, '{}', '{}', '{}', '{}');"""
        
        rental_insert_template = """
        INSERT INTO rental_properties (
            id, category, building_name, address, building_age, underground_floors, aboveground_floors, start_floor, end_floor, rent, 
            management_fee, deposit, key_money, layout, area, url
        ) VALUES ({}, '{}', '{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, '{}', {}, '{}');
        """
        
        rental_id = 1
        data_count = 0

        for row in reader:
            data_count += 1
            
            # total_floorsの処理（地下と地上に分ける）
            underground_floors, aboveground_floors = parse_total_floors(row['階数'])
            
            # floorの処理（ハイフンを含む場合は分割）
            start_floor, end_floor = parse_floor(row['階'])

            # rental_properties テーブルのINSERT文生成
            rental_insert_statement = rental_insert_template.format(
                rental_id,
                row['カテゴリ'].replace("'", "''"),
                row['建物名'].replace("'", "''"),
                row['住所'].replace("'", "''"),
                row['築年数'].replace("'", "''").replace('新築', '0').replace('築', '').replace('年', '').replace('以上', ''),
                underground_floors,  # 地下階数
                aboveground_floors,  # 地上階数
                start_floor,  # 開始階数
                end_floor,  # 終了階数
                round(float(row['家賃'].replace('万円', '').replace('-', '0')) * 10000, 2),
                round(float(row['管理費'].replace('円', '').replace(',', '').replace('-', '0')), 2),
                round(float(row['敷金'].replace('万円', '').replace('-', '0')) * 10000, 2),
                round(float(row['礼金'].replace('万円', '').replace('-', '0')) * 10000, 2),
                row['間取り'].replace("'", "''"),
                round(float(row['面積'].replace('m2', '')), 2),
                row['URL'].replace("'", "''")
            )
            rental_sqlfile.write(rental_insert_statement + '\n')
            print(f"Processed rental property {rental_id}: {row['建物名']}")  # ログ出力
            
            process_station(row.get('最寄り駅1'), rental_id, station_insert_template, station_sqlfile, data_count, 1)
            process_station(row.get('最寄り駅2'), rental_id, station_insert_template, station_sqlfile, data_count, 2)
            process_station(row.get('最寄り駅3'), rental_id, station_insert_template, station_sqlfile, data_count, 3)

            rental_id += 1


def parse_total_floors(total_floors_str):
    """
    地下と地上の階数を解析して分ける関数。
    '地下1地上18' などのデータを地下階数と地上階数に分ける。
    '平屋' の場合は地上階数を1、地下階数を0として処理。
    """
    underground_floors = 0
    aboveground_floors = 0
    
    # 平屋の場合
    if '平屋' in total_floors_str:
        aboveground_floors = 1  # 平屋は1階建てとして処理
    elif '地下' in total_floors_str and '地上' in total_floors_str:
        underground_match = re.search(r'地下(\d+)', total_floors_str)
        aboveground_match = re.search(r'地上(\d+)', total_floors_str)
        underground_floors = int(underground_match.group(1)) if underground_match else 0
        aboveground_floors = int(aboveground_match.group(1)) if aboveground_match else 0
    else:
        # 数値のみの場合
        aboveground_floors_str = re.sub(r'\D', '', total_floors_str)  # 数字のみを抽出
        aboveground_floors = int(aboveground_floors_str) if aboveground_floors_str else 0
    
    return underground_floors, aboveground_floors


def parse_floor(floor_str):
    """
    階（物件の階）を解析して開始階数と終了階数に分ける関数。
    '1-3階' などのデータを開始階数と終了階数に分ける。
    '-' などのデータは、開始階数と終了階数に0またはNULLを設定する。
    """
    if floor_str == '-' or not floor_str.strip():
        start_floor = 0
        end_floor = 0
    elif '-' in floor_str:
        # ハイフンで分割された各値から数字部分を抽出
        floors = floor_str.split('-')
        start_floor_str = re.sub(r'\D', '', floors[0])  # 数字以外を削除
        end_floor_str = re.sub(r'\D', '', floors[1])    # 数字以外を削除
        # 数字部分が抽出できない場合にデフォルト値を設定
        start_floor = int(start_floor_str) if start_floor_str.isdigit() else 0
        end_floor = int(end_floor_str) if end_floor_str.isdigit() else 0
    else:
        # ハイフンがない場合は単一の値として処理し、数字部分だけを抽出
        floor_str_cleaned = re.sub(r'\D', '', floor_str)
        start_floor = int(floor_str_cleaned) if floor_str_cleaned.isdigit() else 0
        end_floor = start_floor
    
    return start_floor, end_floor


def process_station(station_data, rental_id, insert_template, station_sqlfile, data_count, station_num):
    """
    最寄駅のデータを処理し、route_station が2つの要素でない場合はエラーとして処理する。
    """
    if station_data:
        route_station = station_data.split('/')
        
        if len(route_station) != 2:
            print(f"Error: Invalid station data at data {data_count}, station {station_num}: {station_data}")
            return
        
        print(f"Processing data {data_count}, station {station_num}: {route_station}")
        
        # 駅名と移動手段を分離する
        station_info = route_station[1].split()
        
        if len(station_info) < 2:
            print(f"Error: Invalid station format at data {data_count}, station {station_num}: {station_data}")
            return

        station_name = station_info[0]  # 駅名
        transport_mode, time_required = parse_transport_time(station_info[1])  # 移動手段と所要時間を解析
        
        if transport_mode not in ['歩', 'バス', '車']:
            print(f"Skipping station {station_num} due to invalid transport mode: {transport_mode}")
            return
        
        station_insert_statement = insert_template.format(
            rental_id,
            route_station[0].replace("'", "''"),  # 路線名
            station_name.replace("'", "''"),  # 駅名
            transport_mode,  # 移動手段
            time_required  # 所要時間
        )
        station_sqlfile.write(station_insert_statement + '\n')


def parse_transport_time(station_info):
    """移動手段と所要時間を解析する関数"""
    match = re.search(r'(\D+)(\d+)', station_info)
    if match:
        transport_mode = match.group(1).strip()
        time_required = match.group(2).strip()
        return transport_mode, time_required
    else:
        return 'unknown', 'unknown'


generate_insert_statements()