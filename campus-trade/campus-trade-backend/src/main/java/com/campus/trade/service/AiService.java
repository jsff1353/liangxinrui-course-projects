package com.campus.trade.service;

import com.campus.trade.dto.AiMessage;
import com.campus.trade.vo.AiChatVO;

import java.util.List;

public interface AiService {

    /**
     * 智能导购智能体：多轮对话 + Function Calling。
     * 模型只负责理解意图、决定查什么，商品数据一律由后端查库，不允许模型自己编。
     * 未配置大模型 Key 时自动降级为关键词检索，前端体验不变。
     */
    AiChatVO chat(List<AiMessage> messages);

    /** 智能发布助手：根据标题生成商品描述 */
    String generateDescription(String title, String category, Integer itemCondition);
}
