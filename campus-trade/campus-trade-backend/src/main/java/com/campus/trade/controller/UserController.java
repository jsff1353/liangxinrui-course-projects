package com.campus.trade.controller;

import com.campus.trade.common.Result;
import com.campus.trade.common.UserContext;
import com.campus.trade.dto.LoginDTO;
import com.campus.trade.dto.RegisterDTO;
import com.campus.trade.entity.User;
import com.campus.trade.service.UserService;
import com.campus.trade.vo.LoginVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    /** 注册：POST /api/user/register */
    @PostMapping("/register")
    public Result<Void> register(@Valid @RequestBody RegisterDTO dto) {
        userService.register(dto);
        return Result.ok();
    }

    /** 登录：POST /api/user/login，返回 JWT token */
    @PostMapping("/login")
    public Result<LoginVO> login(@Valid @RequestBody LoginDTO dto) {
        return Result.ok(userService.login(dto));
    }

    /** 个人信息：GET /api/user/info，需要请求头带 token */
    @GetMapping("/info")
    public Result<User> info() {
        return Result.ok(userService.getInfo(UserContext.get()));
    }
}
