package com.campus.trade.common;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 标在 Controller 类或方法上，表示只有 role=1 的管理员能访问。
 * <p>
 * 具体校验在 JwtInterceptor 里做（见 AdminOnly 的判断分支）。
 * 不用 Spring Security 注解是因为本项目没引整套安全框架，
 * 一个注解 + 拦截器就能覆盖全部管理接口，比每个方法手写 if 更不容易漏。
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface AdminOnly {
}
