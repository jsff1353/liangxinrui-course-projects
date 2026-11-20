package com.campus.trade.vo;

import lombok.Data;

/**
 * 登录成功后返回给前端的信息。
 * 带 role 是为了让前端能区分管理员和学生，决定显示哪个菜单。
 */
@Data
public class LoginVO {

    private String token;

    private Long userId;

    private String username;

    private String nickname;

    private String avatar;

    private String campus;

    /** 0学生 1管理员 */
    private Integer role;
}
