package com.campus.trade.interceptor;

import com.campus.trade.common.AdminOnly;
import com.campus.trade.common.Result;
import com.campus.trade.common.UserContext;
import com.campus.trade.entity.User;
import com.campus.trade.mapper.UserMapper;
import com.campus.trade.utils.JwtUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * 登录校验拦截器：只认请求头 Authorization: Bearer &lt;token&gt;。
 * <p>
 * 它做三件事：
 * 1. 解析 token 拿到 userId；
 * 2. 每次请求查一次库，确认账号仍存在且未被禁用（禁用即时生效，不用等 token 过期）；
 * 3. 把 userId 放进 UserContext（"你是谁"），若目标标了 {@link AdminOnly} 再校验 role=1（"你能不能"）。
 * <p>
 * 为什么不把 status / role 直接放进 JWT？那样管理员禁用账号或降权后，旧 token 里仍是旧状态，
 * 必须等 24 小时过期才生效。每次查一次库最贵也就几毫秒，安全上更划算。
 */
@Component
@RequiredArgsConstructor
public class JwtInterceptor implements HandlerInterceptor {

    private final JwtUtil jwtUtil;
    private final ObjectMapper objectMapper;
    private final UserMapper userMapper;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        // 浏览器跨域预检请求不带 token，必须放行，否则前端所有请求都会被 401
        if (HttpMethod.OPTIONS.matches(request.getMethod())) {
            return true;
        }

        String header = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (header == null || !header.startsWith("Bearer ")) {
            return reject(response, HttpServletResponse.SC_UNAUTHORIZED, "未登录，请先登录");
        }

        Long userId;
        try {
            userId = jwtUtil.parseUserId(header.substring(7));
        } catch (Exception e) {
            // token 过期 / 被篡改 / 格式错误
            return reject(response, HttpServletResponse.SC_UNAUTHORIZED, "登录状态已失效，请重新登录");
        }

        // 每次请求都查一次库校验账号状态：JWT 里只有 userId，无法表达"已被禁用/已删除"。
        // 只在 needAdmin 时才查库的话，管理员禁用某用户后，他手里的旧 token 仍能正常用满 24 小时。
        // 一次主键查询只有几毫秒，换来"禁用即时生效"，安全上划算。
        User user = userMapper.selectById(userId);
        if (user == null) {
            return reject(response, HttpServletResponse.SC_UNAUTHORIZED, "账号不存在，请重新登录");
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            return reject(response, HttpServletResponse.SC_FORBIDDEN, "账号已被禁用，请联系管理员");
        }
        UserContext.set(userId);

        if (needAdmin(handler) && (user.getRole() == null || user.getRole() != 1)) {
            return reject(response, HttpServletResponse.SC_FORBIDDEN, "需要管理员权限");
        }
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        // 必须清理，避免 Tomcat 线程复用导致下一个请求拿到上一个用户
        UserContext.clear();
    }

    /** 方法上或类上有 @AdminOnly 就需要管理员身份 */
    private boolean needAdmin(Object handler) {
        if (!(handler instanceof HandlerMethod handlerMethod)) {
            return false;
        }
        return handlerMethod.getMethodAnnotation(AdminOnly.class) != null
                || handlerMethod.getBeanType().isAnnotationPresent(AdminOnly.class);
    }

    private boolean reject(HttpServletResponse response, int status, String msg) throws Exception {
        response.setStatus(status);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write(objectMapper.writeValueAsString(Result.fail(status, msg)));
        return false;
    }
}
