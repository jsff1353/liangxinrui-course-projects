package com.campus.trade.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.common.BizException;
import com.campus.trade.dto.LoginDTO;
import com.campus.trade.dto.RegisterDTO;
import com.campus.trade.entity.User;
import com.campus.trade.mapper.UserMapper;
import com.campus.trade.service.UserService;
import com.campus.trade.utils.JwtUtil;
import com.campus.trade.vo.LoginVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserMapper userMapper;
    private final JwtUtil jwtUtil;
    private final BCryptPasswordEncoder passwordEncoder;

    @Override
    public void register(RegisterDTO dto) {
        Long count = userMapper.selectCount(
                new LambdaQueryWrapper<User>().eq(User::getUsername, dto.getUsername()));
        if (count > 0) {
            throw new BizException("用户名已存在");
        }

        User user = new User();
        user.setUsername(dto.getUsername());
        // 入库即加密，库里再也查不到明文
        user.setPassword(passwordEncoder.encode(dto.getPassword()));
        user.setNickname(StringUtils.hasText(dto.getNickname()) ? dto.getNickname() : dto.getUsername());
        user.setPhone(dto.getPhone());
        user.setCampus(dto.getCampus());
        user.setRole(0);
        user.setStatus(1);
        userMapper.insert(user);
    }

    @Override
    public LoginVO login(LoginDTO dto) {
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>().eq(User::getUsername, dto.getUsername()));

        // 用户不存在和密码错误返回同一句提示，避免被用来枚举账号
        if (user == null) {
            throw new BizException("用户名或密码错误");
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            throw new BizException("该账号已被禁用，请联系管理员");
        }

        String stored = user.getPassword();
        boolean isBcrypt = isBcrypt(stored);
        boolean matched = isBcrypt
                ? passwordEncoder.matches(dto.getPassword(), stored)
                : stored.equals(dto.getPassword());

        if (!matched) {
            throw new BizException("用户名或密码错误");
        }

        // 渐进式迁移：库里还是明文的，登录成功后顺手加密回写，老账号不用重置密码
        if (!isBcrypt) {
            User upgrade = new User();
            upgrade.setId(user.getId());
            upgrade.setPassword(passwordEncoder.encode(dto.getPassword()));
            userMapper.updateById(upgrade);
        }

        LoginVO vo = new LoginVO();
        vo.setToken(jwtUtil.createToken(user.getId()));
        vo.setUserId(user.getId());
        vo.setUsername(user.getUsername());
        vo.setNickname(user.getNickname());
        vo.setAvatar(user.getAvatar());
        vo.setCampus(user.getCampus());
        vo.setRole(user.getRole() == null ? 0 : user.getRole());
        return vo;
    }

    @Override
    public User getInfo(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BizException("用户不存在");
        }
        // 密码字段加了 @JsonIgnore，这里不需要再手动 setPassword(null)
        return user;
    }

    @Override
    public Page<User> adminPage(int pageNum, int pageSize, String keyword) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        if (StringUtils.hasText(keyword)) {
            // 用户名或昵称命中都算，外层 and() 保证 or 不会把其他条件带跑
            wrapper.and(w -> w.like(User::getUsername, keyword).or().like(User::getNickname, keyword));
        }
        wrapper.orderByDesc(User::getCreateTime);
        Page<User> page = userMapper.selectPage(new Page<>(pageNum, pageSize), wrapper);
        // 密码字段有 @JsonIgnore，返回给前端是安全的，这里不用手动清
        return page;
    }

    @Override
    public void changeStatus(Long userId, Integer status, Long operatorId) {
        if (status == null || (status != 0 && status != 1)) {
            throw new BizException("状态只能是 0 禁用 / 1 启用");
        }
        if (userId != null && userId.equals(operatorId)) {
            // 管理员把自己禁了，就没人能再进后台解禁了
            throw new BizException("不能禁用自己的账号");
        }
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BizException(404, "用户不存在");
        }
        if (user.getRole() != null && user.getRole() == 1) {
            throw new BizException("不能修改其他管理员的账号状态");
        }
        User update = new User();
        update.setId(userId);
        update.setStatus(status);
        userMapper.updateById(update);
    }

    /** BCrypt 密文固定以 $2a$ / $2b$ / $2y$ 开头，明文不会长这样 */
    private boolean isBcrypt(String pwd) {
        return pwd != null && (pwd.startsWith("$2a$") || pwd.startsWith("$2b$") || pwd.startsWith("$2y$"));
    }
}
