package com.campus.trade.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class RegisterDTO {

    @NotBlank(message = "请输入用户名")
    @Size(min = 3, max = 20, message = "用户名长度需在 3~20 位之间")
    @Pattern(regexp = "^[A-Za-z0-9_]+$", message = "用户名只能包含字母、数字和下划线")
    private String username;

    @NotBlank(message = "请输入密码")
    @Size(min = 6, max = 20, message = "密码长度需在 6~20 位之间")
    private String password;

    @Size(max = 20, message = "昵称最长 20 个字符")
    private String nickname;

    /** 选填，注册时一并录入，省得再进个人中心填 */
    @Size(max = 20, message = "手机号格式不正确")
    private String phone;

    @Size(max = 50, message = "校区名称过长")
    private String campus;
}
