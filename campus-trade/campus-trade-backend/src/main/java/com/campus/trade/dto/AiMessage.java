package com.campus.trade.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 一条对话消息。前端把完整历史一起发过来，后端不存会话，
 * 这样服务端无状态、重启不丢上下文、也不占内存。
 */
@Data
public class AiMessage {

    /** user / assistant 两种，system 由后端自己拼，前端传了也会被忽略 */
    @NotBlank(message = "角色不能为空")
    @Pattern(regexp = "^(user|assistant)$", message = "角色只能是 user 或 assistant")
    private String role;

    @NotBlank(message = "消息内容不能为空")
    @Size(max = 500, message = "单条消息不要超过 500 字")
    private String content;
}
