package com.campus.trade.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

/**
 * 只注册一个 BCrypt 编码器，不引入 Spring Security 的过滤器链。
 * 原因：引 spring-boot-starter-security 会让所有接口默认 401 跳登录页，
 * 还要额外写 SecurityFilterChain 放行，对一个课程设计来说没必要。
 */
@Configuration
public class PasswordConfig {

    /**
     * strength = 10 是默认值，约 50~100ms 一次，安全性与性能的平衡点。
     * BCrypt 每次加密会随机生成盐，所以同一密码两次加密结果不同，必须用 matches() 比对。
     */
    @Bean
    public BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(10);
    }
}
