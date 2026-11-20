-- ============================================================
-- 校园智能二手交易平台  数据库初始化脚本
-- MySQL 8.0+   执行方式：mysql -uroot -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS campus_trade
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE campus_trade;

-- ------------------------------------------------------------
-- 1. 用户表
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    `username`    VARCHAR(50)  NOT NULL                COMMENT '登录账号',
    `password`    VARCHAR(100) NOT NULL                COMMENT '密码(演示用明文, 后续建议 BCrypt)',
    `nickname`    VARCHAR(50)  DEFAULT NULL            COMMENT '昵称',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT = '用户表';

-- ------------------------------------------------------------
-- 2. 商品表
-- status: 0-已下架  1-在售  2-已售出
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `goods`;
CREATE TABLE `goods` (
    `id`          BIGINT        NOT NULL AUTO_INCREMENT COMMENT '主键',
    `user_id`     BIGINT        NOT NULL                COMMENT '发布者(卖家)ID',
    `title`       VARCHAR(100)  NOT NULL                COMMENT '商品标题',
    `description` TEXT          DEFAULT NULL            COMMENT '商品描述',
    `price`       DECIMAL(10,2) NOT NULL                COMMENT '价格',
    `cover_img`   VARCHAR(255)  DEFAULT NULL            COMMENT '封面图URL',
    `category`    VARCHAR(50)   DEFAULT NULL            COMMENT '分类(如: 教材/数码/生活用品)',
    `status`      TINYINT       NOT NULL DEFAULT 1      COMMENT '状态: 0下架 1在售 2已售出',
    `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_category` (`category`),
    KEY `idx_status_create` (`status`, `create_time`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT = '商品表';

-- ------------------------------------------------------------
-- 3. 订单表
-- status: 0-待支付  1-已支付  2-已完成  3-已取消
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
    `id`          BIGINT        NOT NULL AUTO_INCREMENT COMMENT '主键',
    `order_no`    VARCHAR(32)   NOT NULL                COMMENT '订单号(业务唯一)',
    `buyer_id`    BIGINT        NOT NULL                COMMENT '买家ID',
    `seller_id`   BIGINT        NOT NULL                COMMENT '卖家ID',
    `goods_id`    BIGINT        NOT NULL                COMMENT '商品ID',
    `amount`      DECIMAL(10,2) NOT NULL                COMMENT '订单金额',
    `status`      TINYINT       NOT NULL DEFAULT 0      COMMENT '状态: 0待支付 1已支付 2已完成 3已取消',
    `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_no` (`order_no`),
    KEY `idx_buyer_id` (`buyer_id`),
    KEY `idx_seller_id` (`seller_id`),
    KEY `idx_goods_id` (`goods_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT = '订单表';
