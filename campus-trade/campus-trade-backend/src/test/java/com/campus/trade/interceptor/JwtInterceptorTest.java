package com.campus.trade.interceptor;

import com.campus.trade.common.UserContext;
import com.campus.trade.entity.User;
import com.campus.trade.mapper.UserMapper;
import com.campus.trade.utils.JwtUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.http.HttpHeaders;
import org.springframework.web.method.HandlerMethod;

import java.io.PrintWriter;
import java.io.StringWriter;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

/** JWT 拦截器测试：覆盖禁用账号即时失效、token 解析失败、正常放行。 */
@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class JwtInterceptorTest {

    @Mock private JwtUtil jwtUtil;
    @Mock private UserMapper userMapper;
    @Mock private HttpServletRequest request;
    @Mock private HttpServletResponse response;
    @Mock private HandlerMethod handlerMethod;
    @Mock private PrintWriter writer;

    private JwtInterceptor interceptor;
    private StringWriter responseBody;

    @BeforeAll
    static void init() {
        com.campus.trade.service.impl.LambdaCacheInit.init();
    }

    @BeforeEach
    void setUp() throws Exception {
        interceptor = new JwtInterceptor(jwtUtil, new ObjectMapper(), userMapper);
        responseBody = new StringWriter();
        when(request.getMethod()).thenReturn("GET");
        when(request.getHeader(HttpHeaders.AUTHORIZATION)).thenReturn("Bearer test-token");
        when(response.getWriter()).thenReturn(new PrintWriter(responseBody));
        // needAdmin() 会读 handlerMethod 的方法与类，stub 掉避免 NPE
        when(handlerMethod.getBeanType()).thenReturn((Class) Object.class);
        when(handlerMethod.getMethodAnnotation(com.campus.trade.common.AdminOnly.class)).thenReturn(null);
    }

    @AfterEach
    void tearDown() {
        UserContext.clear();
    }

    private User user(int status, int role) {
        User u = new User();
        u.setId(2L);
        u.setStatus(status);
        u.setRole(role);
        return u;
    }

    @Test
    @DisplayName("正常用户放行，并把 userId 放进上下文")
    void normalUserPasses() throws Exception {
        when(jwtUtil.parseUserId(anyString())).thenReturn(2L);
        when(userMapper.selectById(2L)).thenReturn(user(1, 0));

        boolean pass = interceptor.preHandle(request, response, handlerMethod);

        assertThat(pass).isTrue();
        assertThat(UserContext.get()).isEqualTo(2L);
        verify(userMapper).selectById(2L);
    }

    @Test
    @DisplayName("被禁用用户的旧 token 立即被拒（不必等 24 小时过期）")
    void disabledUserRejected() throws Exception {
        when(jwtUtil.parseUserId(anyString())).thenReturn(2L);
        when(userMapper.selectById(2L)).thenReturn(user(0, 0)); // status=0 禁用

        boolean pass = interceptor.preHandle(request, response, handlerMethod);

        assertThat(pass).isFalse();
        verify(response).setStatus(HttpServletResponse.SC_FORBIDDEN);
    }

    @Test
    @DisplayName("账号已被删除时旧 token 被拒")
    void deletedUserRejected() throws Exception {
        when(jwtUtil.parseUserId(anyString())).thenReturn(2L);
        when(userMapper.selectById(2L)).thenReturn(null);

        boolean pass = interceptor.preHandle(request, response, handlerMethod);

        assertThat(pass).isFalse();
        verify(response).setStatus(HttpServletResponse.SC_UNAUTHORIZED);
    }

    @Test
    @DisplayName("token 解析失败被拒，且不查库")
    void badTokenRejected() throws Exception {
        when(jwtUtil.parseUserId(anyString())).thenThrow(new RuntimeException("expired"));

        boolean pass = interceptor.preHandle(request, response, handlerMethod);

        assertThat(pass).isFalse();
        verify(response).setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        verify(userMapper, never()).selectById(anyLong());
    }

    @Test
    @DisplayName("请求结束后清理上下文，避免线程复用串号")
    void cleansContextAfterCompletion() {
        UserContext.set(2L);
        interceptor.afterCompletion(request, response, handlerMethod, null);
        assertThat(UserContext.get()).isNull();
    }
}
