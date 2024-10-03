USE performance_study;

DROP TABLE IF EXISTS rental_properties;
CREATE TABLE rental_properties (
    id INT,
    category VARCHAR(255),
    building_name VARCHAR(255),
    address VARCHAR(255),
    building_age INT,  -- 築年数
    underground_floors INT,  -- 地下階数
    aboveground_floors INT,  -- 地上階数
    start_floor INT,  -- 開始階数
    end_floor INT,  -- 終了階数
    rent DECIMAL(10, 2),  -- 家賃 (円単位)
    management_fee DECIMAL(10, 2),  -- 管理費 (円単位)
    deposit DECIMAL(10, 2),  -- 敷金 (円単位)
    key_money DECIMAL(10, 2),  -- 礼金 (円単位)
    layout VARCHAR(50),  -- 間取り
    area DECIMAL(10, 2),  -- 面積 (平方メートル)
    url TEXT
);

DROP TABLE IF EXISTS nearest_stations;
CREATE TABLE nearest_stations (
    rental_property_id INT NOT NULL,  -- rental_propertiesのIDを外部キーとして使用
    route_name VARCHAR(255) NOT NULL,  -- 路線名
    station_name VARCHAR(255) NOT NULL,  -- 駅名
    transport_mode VARCHAR(50),  -- 移動手段 (例: 歩き, バス)
    time_required INT NOT NULL  -- 所要時間 (分単位)
);
