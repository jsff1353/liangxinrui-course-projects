package com.campus.trade.vo;

import lombok.Data;

import java.math.BigDecimal;

/**
 * 管理端首页统计数据，对应论文里的"借阅/交易统计分析"模块。
 */
@Data
public class AdminStatsVO {

    /** 注册用户数 */
    private long userCount;

    /** 商品总数 */
    private long goodsCount;

    /** 在售商品数 */
    private long onSaleCount;

    /** 订单总数 */
    private long orderCount;

    /** 已完成订单数 */
    private long finishedCount;

    /** 累计成交金额（已付款 + 已完成） */
    private BigDecimal tradeAmount;

    /** 今日新增订单 */
    private long todayOrderCount;
}
