-- ============================================================
-- 校园智能二手交易平台  数据库增量升级脚本 V2
-- 用途：你本机 campus_trade 库已有 8 条商品数据，用这个脚本升级，不丢数据
--
-- 执行方式：mysql -uroot -p campus_trade < upgrade_v2.sql
--
-- ⚠️ 注意：MySQL 8.0 不支持 ADD COLUMN IF NOT EXISTS（那是 MariaDB 语法）
--    所以本脚本【只能执行一次】。若报 Duplicate column name，说明该字段已加过，
--    跳过那一句继续执行后面的即可，不影响数据。
-- ============================================================

USE campus_trade;

SET NAMES utf8mb4;

-- ------------------------------------------------------------
-- 1. sys_user 补字段
-- ------------------------------------------------------------
ALTER TABLE `sys_user`
    ADD COLUMN `avatar`      VARCHAR(255) DEFAULT NULL COMMENT '头像URL' AFTER `nickname`,
    ADD COLUMN `phone`       VARCHAR(20)  DEFAULT NULL COMMENT '联系电话' AFTER `avatar`,
    ADD COLUMN `campus`      VARCHAR(50)  DEFAULT NULL COMMENT '所在校区' AFTER `phone`,
    ADD COLUMN `role`        TINYINT      NOT NULL DEFAULT 0 COMMENT '角色: 0学生 1管理员' AFTER `campus`,
    ADD COLUMN `status`      TINYINT      NOT NULL DEFAULT 1 COMMENT '状态: 0禁用 1正常' AFTER `role`,
    ADD COLUMN `update_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间' AFTER `create_time`,
    ADD KEY `idx_role` (`role`);

-- ------------------------------------------------------------
-- 2. goods 补字段
-- 注意：成色字段用 item_condition，不能叫 condition（MySQL 保留字）
-- ------------------------------------------------------------
ALTER TABLE `goods`
    ADD COLUMN `original_price` DECIMAL(10,2) DEFAULT NULL COMMENT '原价' AFTER `price`,
    ADD COLUMN `item_condition` TINYINT       NOT NULL DEFAULT 2 COMMENT '成色: 1全新 2九成新 3七成新 4五成新及以下' AFTER `category`,
    ADD COLUMN `trade_place`    VARCHAR(100)  DEFAULT NULL COMMENT '期望交易地点' AFTER `item_condition`,
    ADD COLUMN `contact`        VARCHAR(50)   DEFAULT NULL COMMENT '联系方式' AFTER `trade_place`,
    ADD COLUMN `view_count`     INT           NOT NULL DEFAULT 0 COMMENT '浏览量' AFTER `contact`,
    ADD COLUMN `update_time`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间' AFTER `create_time`,
    ADD KEY `idx_title` (`title`);

-- ------------------------------------------------------------
-- 3. orders 补字段
-- ------------------------------------------------------------
ALTER TABLE `orders`
    ADD COLUMN `remark`        VARCHAR(255) DEFAULT NULL COMMENT '买家留言' AFTER `amount`,
    ADD COLUMN `pay_time`      DATETIME     DEFAULT NULL COMMENT '付款时间' AFTER `status`,
    ADD COLUMN `finish_time`   DATETIME     DEFAULT NULL COMMENT '完成时间' AFTER `pay_time`,
    ADD COLUMN `cancel_reason` VARCHAR(255) DEFAULT NULL COMMENT '取消原因' AFTER `finish_time`,
    ADD COLUMN `update_time`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间' AFTER `create_time`,
    ADD KEY `idx_status_create` (`status`, `create_time`);

-- ------------------------------------------------------------
-- 4. 补管理员账号 + 演示学生账号
-- 密码 123456 为明文，首次登录成功后后端会自动升级成 BCrypt 密文
-- INSERT IGNORE：账号已存在就跳过，不会报错
-- ------------------------------------------------------------
INSERT IGNORE INTO `sys_user` (`username`, `password`, `nickname`, `phone`, `campus`, `role`, `status`)
VALUES ('admin',  '123456', '系统管理员', '13800000000', '科教城校区', 1, 1),
       ('stu001', '123456', '李同学',     '13800000001', '科教城校区', 0, 1),
       ('stu002', '123456', '王同学',     '13800000002', '科教城校区', 0, 1);

-- ------------------------------------------------------------
-- 5. 给已有 8 条商品补默认成色与交易地点（可跳过，纯美化演示数据）
-- 按 id 顺序轮着填成色 1/2/3，避免列表里全是同一个标签
-- ------------------------------------------------------------
-- 每条都带 WHERE，避免 DBeaver / Workbench 开启 safe update mode 时报
-- "You are using safe update mode" 拒绝执行
UPDATE `goods` SET `trade_place` = '图书馆门口' WHERE `trade_place` IS NULL AND `id` > 0;
UPDATE `goods` SET `view_count` = 60 + `id` * 13 WHERE `view_count` = 0 AND `id` > 0;
UPDATE `goods` SET `item_condition` = 2 WHERE `id` % 3 = 1;
UPDATE `goods` SET `item_condition` = 3 WHERE `id` % 3 = 2;
UPDATE `goods` SET `item_condition` = 1 WHERE `id` % 3 = 0;

-- ------------------------------------------------------------
-- 6. 校验：确认字段都加上了
-- ------------------------------------------------------------
SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'campus_trade'
  AND TABLE_NAME IN ('sys_user', 'goods', 'orders')
ORDER BY TABLE_NAME, ORDINAL_POSITION;
