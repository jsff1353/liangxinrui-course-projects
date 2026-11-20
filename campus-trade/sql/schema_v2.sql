-- ============================================================
-- 校园智能二手交易平台  数据库初始化脚本 V2（全新建库用）
-- MySQL 8.0+   执行方式：mysql -uroot -p < schema_v2.sql
--
-- 用法说明：
--   1. 本脚本会 DROP 重建三张表，仅用于【空库/全新环境】
--   2. 你本机已有 8 条商品数据的，请改用 upgrade_v2.sql（增量，不丢数据）
--   3. 密码字段先存明文 123456，首次登录成功后由后端自动升级为 BCrypt 密文
-- ============================================================

CREATE DATABASE IF NOT EXISTS campus_trade
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE campus_trade;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. 用户表
-- role: 0-学生(普通用户)  1-管理员
-- status: 0-禁用  1-正常
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT           COMMENT '主键',
    `username`    VARCHAR(50)  NOT NULL                          COMMENT '登录账号(学号/工号)',
    `password`    VARCHAR(100) NOT NULL                          COMMENT '密码: 明文兼容期 -> BCrypt($2a$开头40+位)',
    `nickname`    VARCHAR(50)  DEFAULT NULL                      COMMENT '昵称',
    `avatar`      VARCHAR(255) DEFAULT NULL                      COMMENT '头像URL',
    `phone`       VARCHAR(20)  DEFAULT NULL                      COMMENT '联系电话',
    `campus`      VARCHAR(50)  DEFAULT NULL                      COMMENT '所在校区',
    `role`        TINYINT      NOT NULL DEFAULT 0                COMMENT '角色: 0学生 1管理员',
    `status`      TINYINT      NOT NULL DEFAULT 1                COMMENT '状态: 0禁用 1正常',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    `update_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_role` (`role`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT = '用户表(学生/管理员)';

-- ------------------------------------------------------------
-- 2. 商品表
-- status: 0-已下架  1-在售  2-已锁定(有人下单未付款)  3-已售出
-- item_condition: 1-全新  2-九成新  3-七成新  4-五成新及以下
-- 注意: 成色字段不能叫 condition, 那是 MySQL 保留字, 建表会报语法错误
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `goods`;
CREATE TABLE `goods` (
    `id`             BIGINT        NOT NULL AUTO_INCREMENT      COMMENT '主键',
    `user_id`        BIGINT        NOT NULL                     COMMENT '发布者(卖家)ID',
    `title`          VARCHAR(100)  NOT NULL                     COMMENT '商品标题',
    `description`    TEXT          DEFAULT NULL                 COMMENT '商品描述(AI发布助手生成或手填)',
    `price`          DECIMAL(10,2) NOT NULL                     COMMENT '售价',
    `original_price` DECIMAL(10,2) DEFAULT NULL                 COMMENT '原价(用于展示折扣)',
    `cover_img`      VARCHAR(255)  DEFAULT NULL                 COMMENT '封面图URL',
    `category`       VARCHAR(50)   DEFAULT NULL                 COMMENT '分类: 教材/数码/生活用品/运动/其他',
    `item_condition` TINYINT       NOT NULL DEFAULT 2           COMMENT '成色: 1全新 2九成新 3七成新 4五成新及以下',
    `trade_place`    VARCHAR(100)  DEFAULT NULL                 COMMENT '期望交易地点(校内)',
    `contact`        VARCHAR(50)   DEFAULT NULL                 COMMENT '联系方式(QQ/微信)',
    `view_count`     INT           NOT NULL DEFAULT 0           COMMENT '浏览量',
    `status`         TINYINT       NOT NULL DEFAULT 1           COMMENT '状态: 0已下架 1在售 2已锁定 3已售出',
    `create_time`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    `update_time`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_category` (`category`),
    KEY `idx_status_create` (`status`, `create_time`),
    KEY `idx_title` (`title`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT = '商品表';

-- ------------------------------------------------------------
-- 3. 订单表
-- status: 0-待付款  1-已付款  2-已完成  3-已取消
-- 状态机: 0 -> 1 -> 2 ;  0/1 -> 3(取消)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
    `id`            BIGINT        NOT NULL AUTO_INCREMENT       COMMENT '主键',
    `order_no`      VARCHAR(32)   NOT NULL                      COMMENT '订单号(业务唯一, 如 20261023213000+6位随机)',
    `buyer_id`      BIGINT        NOT NULL                      COMMENT '买家ID',
    `seller_id`     BIGINT        NOT NULL                      COMMENT '卖家ID',
    `goods_id`      BIGINT        NOT NULL                      COMMENT '商品ID',
    `amount`        DECIMAL(10,2) NOT NULL                      COMMENT '订单金额(下单时快照, 不随商品改价变动)',
    `goods_title_snapshot`  VARCHAR(100) DEFAULT NULL          COMMENT '下单时商品标题快照(商品删除后仍可显示)',
    `goods_cover_snapshot`  VARCHAR(255) DEFAULT NULL          COMMENT '下单时商品封面快照',
    `goods_category_snapshot` VARCHAR(50) DEFAULT NULL         COMMENT '下单时商品分类快照',
    `remark`        VARCHAR(255)  DEFAULT NULL                  COMMENT '买家留言',
    `status`        TINYINT       NOT NULL DEFAULT 0            COMMENT '状态: 0待付款 1已付款 2已完成 3已取消',
    `pay_time`      DATETIME      DEFAULT NULL                  COMMENT '付款时间',
    `finish_time`   DATETIME      DEFAULT NULL                  COMMENT '完成时间',
    `cancel_reason` VARCHAR(255)  DEFAULT NULL                  COMMENT '取消原因',
    `create_time`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
    `update_time`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_no` (`order_no`),
    KEY `idx_buyer_id` (`buyer_id`),
    KEY `idx_seller_id` (`seller_id`),
    KEY `idx_goods_id` (`goods_id`),
    KEY `idx_status_create` (`status`, `create_time`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT = '订单表';

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 4. 演示数据
-- 密码统一 123456（明文，首次登录后自动升级为 BCrypt）
-- id 固定写死，方便前端联调时对照
-- ============================================================

INSERT INTO `sys_user` (`id`, `username`, `password`, `nickname`, `phone`, `campus`, `role`, `status`)
VALUES (1, 'admin', '123456', '系统管理员', '13800000000', '科教城校区', 1, 1),
       (2, 'stu001', '123456', '李同学', '13800000001', '科教城校区', 0, 1),
       (3, 'stu002', '123456', '王同学', '13800000002', '科教城校区', 0, 1),
       (4, 'stu003', '123456', '陈同学', '13800000003', '天河校区', 0, 1);

INSERT INTO `goods` (`user_id`, `title`, `description`, `price`, `original_price`, `category`, `item_condition`,
                     `trade_place`, `contact`, `view_count`, `status`)
VALUES (2, '高等数学上册 同济第七版', '大一用过，无笔记，书角轻微磨损，内页干净。适合补考和期末复习。', 15.00, 49.80, '教材', 2, '宿舍楼下菜鸟驿站', 'QQ: 100001', 128, 1),
       (2, '线性代数 同济第六版', '只翻过前两章，几乎全新，无划线。', 12.00, 32.00, '教材', 1, '图书馆门口', 'QQ: 100001', 86, 1),
       (2, 'iPad 2021 第九代 64G WiFi', '2022年买的，一直贴膜带套，电池健康92%，配原装充电器，无维修。', 1350.00, 2499.00, '数码', 2, '教学楼A栋', '微信: li_tongxue', 463, 1),
       (3, '捷安特 ATX660 山地车', '骑了一年多，刚换过链条和刹车皮，车锁一起送。毕业清仓。', 480.00, 1580.00, '运动', 3, '东区宿舍车棚', 'QQ: 200002', 312, 1),
       (3, '宿舍小冰箱 50L', '用了一学年，制冷正常，声音小。太重不好寄，只限校内自提。', 180.00, 399.00, '生活用品', 2, '西区6栋楼下', 'QQ: 200002', 205, 1),
       (3, '罗技 M330 无线鼠标', '买错了型号，只用过一次，包装盒还在。', 45.00, 99.00, '数码', 1, '操场看台', 'QQ: 200002', 74, 1),
       (4, '大学英语四级真题 2023版', '做过前5套，后面全新，答案册完整。', 10.00, 39.80, '教材', 3, '图书馆三楼', '微信: chen_stu', 56, 1),
       (4, '宜家 台灯 LED 可调光', '大二买的，三档亮度都正常，灯泡没换过。', 35.00, 89.00, '生活用品', 2, '南门快递点', '微信: chen_stu', 91, 1),
       (2, '小米 移动电源 10000mAh', '容量正常，能给手机充两次半。外壳有轻微划痕。', 40.00, 129.00, '数码', 3, '食堂二楼', 'QQ: 100001', 133, 1),
       (3, '考研政治 肖秀荣1000题', '2025版，只做了选择题部分，大题空白。', 18.00, 59.80, '教材', 2, '图书馆门口', 'QQ: 200002', 68, 1),
       (4, '篮球 斯伯丁 7号', '室内场用过几次，气足，表皮无明显磨损。', 55.00, 168.00, '运动', 2, '体育馆门口', '微信: chen_stu', 47, 1),
       (2, '收纳箱 大号 带轮 2个', '搬宿舍时买的，两个一起出，轮子完好。', 25.00, 79.00, '生活用品', 2, '东区宿舍车棚', 'QQ: 100001', 39, 1);

-- 一条演示订单：stu001 买了 stu002 的鼠标，已完成
INSERT INTO `orders` (`order_no`, `buyer_id`, `seller_id`, `goods_id`, `amount`, `goods_title_snapshot`, `goods_cover_snapshot`, `goods_category_snapshot`, `remark`, `status`, `pay_time`, `finish_time`)
VALUES ('20261020153000123456', 2, 3, 6, 45.00, '罗技 M330 无线鼠标', NULL, '数码', '明天中午操场看台交易可以吗', 2, '2026-10-20 15:31:00', '2026-10-21 12:10:00');
