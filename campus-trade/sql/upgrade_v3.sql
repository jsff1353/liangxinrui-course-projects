-- ============================================================
-- 校园智能二手交易平台  数据库增量升级脚本 V3
-- 用途：为 orders 表补"商品信息快照"字段。
--       商品被物理删除后，已生成的订单仍能显示当时买的什么。
--
-- 执行方式：mysql -uroot -p campus_trade < upgrade_v3.sql
-- 全新环境请直接用 schema_v2.sql（已含这些字段），不要执行本脚本。
--
-- 注意：MySQL 8.0 不支持 ADD COLUMN IF NOT EXISTS，本脚本只能执行一次；
--       若报 Duplicate column name，说明字段已加过，跳过即可，不影响数据。
-- ============================================================

USE campus_trade;
SET NAMES utf8mb4;

-- 1. orders 补三个快照字段
ALTER TABLE `orders`
    ADD COLUMN `goods_title_snapshot`    VARCHAR(100) DEFAULT NULL COMMENT '下单时商品标题快照' AFTER `amount`,
    ADD COLUMN `goods_cover_snapshot`    VARCHAR(255) DEFAULT NULL COMMENT '下单时商品封面快照' AFTER `goods_title_snapshot`,
    ADD COLUMN `goods_category_snapshot` VARCHAR(50)  DEFAULT NULL COMMENT '下单时商品分类快照' AFTER `goods_cover_snapshot`;

-- 2. 回填历史订单：把当前商品信息写进快照（若商品已被删则保持 NULL，属正常）
UPDATE `orders` o
    INNER JOIN `goods` g ON o.goods_id = g.id
SET o.goods_title_snapshot = g.title,
    o.goods_cover_snapshot = g.cover_img,
    o.goods_category_snapshot = g.category
WHERE o.goods_title_snapshot IS NULL;

-- 3. 校验
SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'campus_trade' AND TABLE_NAME = 'orders'
  AND COLUMN_NAME LIKE '%snapshot%'
ORDER BY ORDINAL_POSITION;
