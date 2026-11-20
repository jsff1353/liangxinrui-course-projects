package com.campus.trade.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.math.BigDecimal;

/**
 * 商品发布 / 编辑共用的请求体。
 * <p>
 * 为什么不让前端直接传 Goods 实体：实体的 userId、status、viewCount 这些字段
 * 由后端决定，如果让前端传，等于把"我是谁""我上不上架"的权限交给了浏览器。
 * DTO 只收用户真正能填的字段。
 */
@Data
public class GoodsDTO {

    /** 编辑时由 URL 路径回填，发布时为空 */
    private Long id;

    @NotBlank(message = "商品标题不能为空")
    @Size(max = 50, message = "标题最多 50 个字")
    private String title;

    @Size(max = 2000, message = "商品描述最多 2000 个字")
    private String description;

    @NotNull(message = "请填写售价")
    @DecimalMin(value = "0.01", message = "售价必须大于 0")
    @Digits(integer = 8, fraction = 2, message = "售价最多两位小数")
    private BigDecimal price;

    /** 原价可选，前端用来展示划线价 */
    @DecimalMin(value = "0", message = "原价不能为负数")
    @Digits(integer = 8, fraction = 2, message = "原价最多两位小数")
    private BigDecimal originalPrice;

    @NotBlank(message = "请选择分类")
    private String category;

    @NotNull(message = "请选择成色")
    @Min(value = 1, message = "成色取值范围为 1~4")
    @Max(value = 4, message = "成色取值范围为 1~4")
    private Integer itemCondition;

    @Size(max = 100, message = "交易地点最多 100 个字")
    private String tradePlace;

    @Size(max = 50, message = "联系方式最多 50 个字")
    private String contact;

    @Size(max = 255, message = "图片地址过长")
    private String coverImg;
}
