package com.campus.trade.service.impl;

import com.campus.trade.common.BizException;
import com.campus.trade.dto.LoginDTO;
import com.campus.trade.dto.RegisterDTO;
import com.campus.trade.entity.User;
import com.campus.trade.vo.LoginVO;
import com.campus.trade.mapper.UserMapper;
import com.campus.trade.utils.JwtUtil;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.*;

/** 用户服务单元测试：覆盖 BCrypt 加密、明文密码渐进迁移、登录失败不枚举账号。 */
@ExtendWith(MockitoExtension.class)
class UserServiceImplTest {

    @Mock private UserMapper userMapper;
    @Mock private JwtUtil jwtUtil;

    private BCryptPasswordEncoder encoder;
    private UserServiceImpl service;

    @BeforeAll
    static void initLambdaCache() {
        LambdaCacheInit.init();
    }

    @BeforeEach
    void setUp() {
        encoder = new BCryptPasswordEncoder();
        service = new UserServiceImpl(userMapper, jwtUtil, encoder);
    }

    private RegisterDTO registerDto() {
        RegisterDTO dto = new RegisterDTO();
        dto.setUsername("stu009");
        dto.setPassword("123456");
        dto.setNickname("张同学");
        return dto;
    }

    private LoginDTO loginDto() {
        LoginDTO dto = new LoginDTO();
        dto.setUsername("stu001");
        dto.setPassword("123456");
        return dto;
    }

    @Test
    @DisplayName("注册：密码以 BCrypt 密文入库，绝不存明文")
    void registerHashesPassword() {
        when(userMapper.selectCount(any())).thenReturn(0L);

        service.register(registerDto());

        ArgumentCaptor<User> cap = ArgumentCaptor.forClass(User.class);
        verify(userMapper).insert(cap.capture());
        User saved = cap.getValue();
        assertThat(saved.getPassword()).isNotEqualTo("123456");
        assertThat(saved.getPassword()).startsWith("$2");
        assertThat(encoder.matches("123456", saved.getPassword())).isTrue();
        assertThat(saved.getRole()).isZero();   // 注册用户一律学生
        assertThat(saved.getStatus()).isEqualTo(1);
    }

    @Test
    @DisplayName("用户名重复时注册失败")
    void registerDuplicateRejected() {
        when(userMapper.selectCount(any())).thenReturn(1L);
        assertThatThrownBy(() -> service.register(registerDto()))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("已存在");
        verify(userMapper, never()).insert(any(User.class));
    }

    @Test
    @DisplayName("BCrypt 密码登录成功并签发 token")
    void loginWithBcrypt() {
        User u = new User();
        u.setId(2L);
        u.setUsername("stu001");
        u.setPassword(encoder.encode("123456"));
        u.setStatus(1);
        u.setRole(0);
        when(userMapper.selectOne(any())).thenReturn(u);
        when(jwtUtil.createToken(2L)).thenReturn("test-token");

        LoginVO vo = service.login(loginDto());

        assertThat(vo.getToken()).isEqualTo("test-token");
        assertThat(vo.getUserId()).isEqualTo(2L);
        verify(userMapper, never()).updateById(any(User.class)); // 密文用户无需迁移
    }

    @Test
    @DisplayName("老库明文密码登录成功后自动升级为 BCrypt")
    void loginMigratesPlainPassword() {
        User u = new User();
        u.setId(2L);
        u.setUsername("stu001");
        u.setPassword("123456"); // 明文
        u.setStatus(1);
        when(userMapper.selectOne(any())).thenReturn(u);
        when(jwtUtil.createToken(2L)).thenReturn("t");

        service.login(loginDto());

        ArgumentCaptor<User> cap = ArgumentCaptor.forClass(User.class);
        verify(userMapper).updateById(cap.capture());
        assertThat(cap.getValue().getPassword()).startsWith("$2");
        assertThat(encoder.matches("123456", cap.getValue().getPassword())).isTrue();
    }

    @Test
    @DisplayName("密码错误与用户不存在返回同一提示，防止枚举账号")
    void loginFailureDoesNotLeakAccount() {
        when(userMapper.selectOne(any())).thenReturn(null);
        assertThatThrownBy(() -> service.login(loginDto()))
                .isInstanceOf(BizException.class)
                .hasMessage("用户名或密码错误");

        User wrong = new User();
        wrong.setId(3L);
        wrong.setPassword(encoder.encode("another-pwd"));
        wrong.setStatus(1);
        when(userMapper.selectOne(any())).thenReturn(wrong);
        assertThatThrownBy(() -> service.login(loginDto()))
                .isInstanceOf(BizException.class)
                .hasMessage("用户名或密码错误");
    }

    @Test
    @DisplayName("被禁用账号无法登录")
    void disabledAccountCannotLogin() {
        User u = new User();
        u.setId(2L);
        u.setPassword(encoder.encode("123456"));
        u.setStatus(0); // 禁用
        when(userMapper.selectOne(any())).thenReturn(u);

        assertThatThrownBy(() -> service.login(loginDto()))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("禁用");
        verify(jwtUtil, never()).createToken(anyLong());
    }
}
