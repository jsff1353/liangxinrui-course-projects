package com.campus.trade.vo;

import com.campus.trade.entity.Order;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 订单列表项：订单本体 + 商品快照标题图 + 双方昵称。
 * 没有这些冗余字段，前端就得为每条订单再发两次请求，列表一卡一卡的。
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class OrderVO extends Order {

    private String goodsTitle;

    private String goodsCover;

    private String goodsCategory;

    private String buyerNickname;

    private String sellerNickname;
}
