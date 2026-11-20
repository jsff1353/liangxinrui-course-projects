package com.campus.trade;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 启动类。
 * @MapperScan 让 MyBatis-Plus 自动为 mapper 包下的接口生成实现。
 * @EnableScheduling 开启定时任务，给超时订单自动取消用。
 */
@SpringBootApplication
@EnableScheduling
@MapperScan("com.campus.trade.mapper")
public class CampusTradeApplication {

    public static void main(String[] args) {
        SpringApplication.run(CampusTradeApplication.class, args);
    }
}
