package com.campus.trade.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 下单入参。
 * 注意这里只有 goodsId，没有 amount / sellerId：
 * 价格和卖家必须由后端从数据库查出来，不然前端改个金额就能 1 块钱买走 iPhone。
 */
@Data
public class OrderCreateDTO {

    @NotNull(message = "缺少商品ID")
    private Long goodsId;

    @Size(max = 255, message = "留言最多 255 个字")
    private String remark;
}
