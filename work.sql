--INSERTの実行確認
SELECT COUNT(*)
FROM rental_properties;
--→190,603ならOK

SELECT COUNT(*)
FROM nearest_stations;
--→549,956ならOK


--全件検索
SELECT *
FROM rental_properties;

SELECT *
FROM nearest_stations;


--ID指定検索
SELECT *
FROM rental_properties
WHERE id = 1;

SELECT *
FROM nearest_stations
WHERE rental_property_id = 1;


--前方一致、部分一致
SELECT *
FROM nearest_stations
WHERE station_name LIKE '品川%';

SELECT *
FROM nearest_stations
WHERE station_name LIKE '%品川%';


--結合
SELECT *
FROM rental_properties
INNER JOIN nearest_stations
ON rental_properties.id = nearest_stations.rental_property_id; --Hashになるはず

SELECT *
FROM rental_properties
INNER JOIN nearest_stations
ON rental_properties.id < nearest_stations.rental_property_id; --Nested Loopになるはず
--→インデックスなしのNested Loopなので激遅のはず


--インデックス作成
CREATE INDEX idx_rental_properties_id ON rental_properties (id);
CREATE INDEX idx_nearest_stations_rental_property_id ON nearest_stations (rental_property_id);


--結合
SELECT *
FROM rental_properties
INNER JOIN nearest_stations
ON rental_properties.id = nearest_stations.rental_property_id; --インデックスがあるのでNested Loopになるはず

SELECT *
FROM rental_properties
INNER JOIN nearest_stations
ON rental_properties.id < nearest_stations.rental_property_id; --Nested Loopになるはず
--→インデックスがあるので早いはず


--前方一致、部分一致
SELECT *
FROM nearest_stations
WHERE station_name LIKE '品川%';

SELECT *
FROM nearest_stations
WHERE station_name LIKE '%品川%';
--→インデックスが使えないはず


--レコード更新のパフォーマンス確認
-- 家賃を更新する
UPDATE rental_properties
SET rent = rent + 1000
WHERE id = 1;


--不要なインデックス作成
CREATE INDEX idx_rental_properties_rent_category ON rental_properties (rent, category);
CREATE INDEX idx_rental_properties_rent_building_name ON rental_properties (rent, building_name);
CREATE INDEX idx_rental_properties_rent_address ON rental_properties (rent, address);
CREATE INDEX idx_rental_properties_rent_building_age ON rental_properties (rent, building_age);
CREATE INDEX idx_rental_properties_rent_floors ON rental_properties (rent, underground_floors, aboveground_floors);
CREATE INDEX idx_rental_properties_rent_floor_range ON rental_properties (rent, start_floor, end_floor);
CREATE INDEX idx_rental_properties_rent_management_fee ON rental_properties (rent, management_fee);
CREATE INDEX idx_rental_properties_rent_deposit ON rental_properties (rent, deposit);
CREATE INDEX idx_rental_properties_rent_key_money ON rental_properties (rent, key_money);
CREATE INDEX idx_rental_properties_rent_area ON rental_properties (rent, area);


--レコード更新のパフォーマンス確認
-- 家賃を更新する
UPDATE rental_properties
SET rent = rent + 1000
WHERE id = 1;