package com.campus.trade.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.List;

@Data
public class AiChatDTO {

    /**
     * 完整对话历史（最后一条是本次用户提问）。
     * 只保留最近 10 轮：对话越长 token 越贵，而且早期内容对导购没什么用。
     */
    @NotEmpty(message = "对话内容不能为空")
    @Size(max = 20, message = "对话太长了，请点击清空重新开始")
    @Valid
    private List<AiMessage> messages;
}
