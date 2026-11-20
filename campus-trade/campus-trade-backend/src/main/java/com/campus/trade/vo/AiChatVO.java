package com.campus.trade.vo;

import com.campus.trade.entity.Goods;
import lombok.Data;

import java.util.List;

/**
 * 智能导购智能体的一次回复。
 * goods 是这一轮通过工具调用查到的真实商品（可能为空，比如用户只是在问流程），
 * 前端把 reply 渲染成气泡、把 goods 渲染成商品卡片。
 */
@Data
public class AiChatVO {

    /** 智能体的自然语言回复 */
    private String reply;

    /** 本轮命中的在售商品 */
    private List<Goods> goods;

    /** true=真正走了大模型；false=未配置 Key 或调用失败，已降级为本地检索 */
    private boolean aiUsed;
}
