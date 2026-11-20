package com.campus.trade.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("goods")
public class Goods {

    /** 商品状态常量，避免代码里到处写魔法数字 */
    public static final int STATUS_OFF = 0;      // 已下架
    public static final int STATUS_ON_SALE = 1;  // 在售
    public static final int STATUS_LOCKED = 2;   // 已锁定(有人下单未付款)
    public static final int STATUS_SOLD = 3;     // 已售出

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 发布者(卖家)ID */
    private Long userId;

    private String title;

    private String description;

    /** 售价 */
    private BigDecimal price;

    /** 原价，用于前端展示"原价 ¥xxx"的划线价 */
    private BigDecimal originalPrice;

    private String coverImg;

    /** 分类: 教材/数码/生活用品/运动/其他 */
    private String category;

    /**
     * 成色: 1全新 2九成新 3七成新 4五成新及以下
     * 注意字段名不能叫 condition，那是 MySQL 保留字
     */
    private Integer itemCondition;

    /** 期望交易地点(校内) */
    private String tradePlace;

    /** 联系方式 */
    private String contact;

    /** 浏览量 */
    private Integer viewCount;

    /** 0已下架 1在售 2已锁定 3已售出 */
    private Integer status;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
