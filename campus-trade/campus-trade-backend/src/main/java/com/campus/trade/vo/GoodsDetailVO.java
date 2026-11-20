package com.campus.trade.vo;

import com.campus.trade.entity.Goods;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 商品详情。
 * <p>
 * 继承 Goods 而不是重新定义一遍字段，好处是：原来前端拿 data.title / data.price
 * 的代码一行都不用改，新增的卖家信息作为额外字段附加在 JSON 里。
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class GoodsDetailVO extends Goods {

    /** 卖家昵称 */
    private String sellerNickname;

    /** 卖家头像 */
    private String sellerAvatar;

    /** 卖家所在校区 */
    private String sellerCampus;

    /** 当前登录人是不是发布者本人（前端据此隐藏"立即购买"） */
    private Boolean mine;

    /** 该商品进行中的订单ID（待付款/已付款），没有则为 null */
    private Long activeOrderId;
}
