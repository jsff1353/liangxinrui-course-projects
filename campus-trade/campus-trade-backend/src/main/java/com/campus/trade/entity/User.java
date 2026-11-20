package com.campus.trade.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("sys_user")
public class User {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String username;

    /**
     * 密码。@JsonIgnore 保证它绝对不会出现在任何接口的 JSON 返回里，
     * 比在 Service 里手写 setPassword(null) 更可靠（漏一个接口就会漏密码）。
     */
    @JsonIgnore
    private String password;

    private String nickname;

    /** 头像URL */
    private String avatar;

    /** 联系电话 */
    private String phone;

    /** 所在校区 */
    private String campus;

    /** 角色: 0学生 1管理员 */
    private Integer role;

    /** 状态: 0禁用 1正常 */
    private Integer status;

    /** 库里由 DEFAULT CURRENT_TIMESTAMP 生成，插入时不传即可 */
    private LocalDateTime createTime;

    /** 库里由 ON UPDATE CURRENT_TIMESTAMP 自动维护 */
    private LocalDateTime updateTime;

    /** 前端用：是否管理员。不映射数据库字段，只作为 JSON 输出方便前端判断 */
    public boolean isAdmin() {
        return role != null && role == 1;
    }
}
