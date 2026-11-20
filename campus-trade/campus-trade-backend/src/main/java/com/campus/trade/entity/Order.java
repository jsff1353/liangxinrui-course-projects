package com.campus.trade.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 订单。表名用的是 orders，不是 order（order 是 SQL 保留字，会直接报错）。
 */
@Data
@TableName("orders")
public class Order {

    public static final int STATUS_UNPAID = 0;    // 待付款
    public static final int STATUS_PAID = 1;      // 已付款
    public static final int STATUS_FINISHED = 2;  // 已完成
    public static final int STATUS_CANCELED = 3;  // 已取消

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 业务订单号，格式：yyyyMMddHHmmss + 6位随机 */
    private String orderNo;

    private Long buyerId;

    private Long sellerId;

    private Long goodsId;

    /** 下单时的金额快照，卖家后续改价不影响已生成的订单 */
    private BigDecimal amount;

    /** 下单时的商品标题快照：商品被删除后订单详情仍能显示买的是什么 */
    private String goodsTitleSnapshot;

    /** 下单时的商品封面快照 */
    private String goodsCoverSnapshot;

    /** 下单时的商品分类快照 */
    private String goodsCategorySnapshot;

    /** 买家留言 */
    private String remark;

    /** 0待付款 1已付款 2已完成 3已取消 */
    private Integer status;

    private LocalDateTime payTime;

    private LocalDateTime finishTime;

    private String cancelReason;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
