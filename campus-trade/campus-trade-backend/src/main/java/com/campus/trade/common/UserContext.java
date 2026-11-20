package com.campus.trade.common;

/**
 * 当前登录用户上下文。
 * 拦截器解析 token 后写入，Controller/Service 直接取，避免信任前端传来的 userId。
 * 注意：请求结束必须 clear()，否则线程池复用会导致用户串号。
 */
public class UserContext {

    private static final ThreadLocal<Long> HOLDER = new ThreadLocal<>();

    public static void set(Long userId) {
        HOLDER.set(userId);
    }

    public static Long get() {
        return HOLDER.get();
    }

    public static void clear() {
        HOLDER.remove();
    }
}
