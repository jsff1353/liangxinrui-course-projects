package com.campus.trade.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.dto.LoginDTO;
import com.campus.trade.dto.RegisterDTO;
import com.campus.trade.entity.User;
import com.campus.trade.vo.LoginVO;

public interface UserService {

    /** 注册，用户名重复会抛异常 */
    void register(RegisterDTO dto);

    /** 登录成功返回 JWT token */
    LoginVO login(LoginDTO dto);

    /** 查询个人信息(不含密码) */
    User getInfo(Long userId);

    /** 管理端：用户分页，可按用户名/昵称模糊搜索 */
    Page<User> adminPage(int pageNum, int pageSize, String keyword);

    /** 管理端：启用(1) / 禁用(0) 账号 */
    void changeStatus(Long userId, Integer status, Long operatorId);
}
