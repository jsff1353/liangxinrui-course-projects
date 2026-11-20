package com.campus.trade.service.impl;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.campus.trade.common.BizException;
import com.campus.trade.dto.GoodsDTO;
import com.campus.trade.entity.Goods;
import com.campus.trade.mapper.GoodsMapper;
import com.campus.trade.mapper.OrderMapper;
import com.campus.trade.mapper.UserMapper;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/** 商品服务单元测试：覆盖后端裁决字段、越权校验、价格校验、锁定状态保护。 */
@ExtendWith(MockitoExtension.class)
class GoodsServiceImplTest {

    @Mock private GoodsMapper goodsMapper;
    @Mock private UserMapper userMapper;
    @Mock private OrderMapper orderMapper;

    private GoodsServiceImpl service;

    @BeforeAll
    static void initLambdaCache() {
        LambdaCacheInit.init();
    }

    @BeforeEach
    void setUp() {
        service = new GoodsServiceImpl(goodsMapper, userMapper, orderMapper);
    }

    private GoodsDTO dto() {
        GoodsDTO dto = new GoodsDTO();
        dto.setTitle("高等数学上册");
        dto.setPrice(new BigDecimal("15.00"));
        dto.setCategory("教材");
        dto.setItemCondition(2);
        return dto;
    }

    @Test
    @DisplayName("发布商品：状态、浏览量、发布者由后端裁决，不采信前端传值")
    void publishUsesServerSideFields() {
        GoodsDTO dto = dto();
        when(goodsMapper.insert(any(Goods.class))).thenReturn(1);

        service.publish(dto, 8L);

        ArgumentCaptor<Goods> cap = ArgumentCaptor.forClass(Goods.class);
        verify(goodsMapper).insert(cap.capture());
        Goods saved = cap.getValue();
        assertThat(saved.getUserId()).isEqualTo(8L);
        assertThat(saved.getStatus()).isEqualTo(Goods.STATUS_ON_SALE);
        assertThat(saved.getViewCount()).isZero();
        assertThat(saved.getTitle()).isEqualTo("高等数学上册");
    }

    @Test
    @DisplayName("原价低于售价时拒绝发布")
    void originalPriceBelowPriceRejected() {
        GoodsDTO dto = dto();
        dto.setOriginalPrice(new BigDecimal("9.00")); // 原价 < 售价 15
        assertThatThrownBy(() -> service.publish(dto, 8L))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("原价不能低于售价");
        verify(goodsMapper, never()).insert(any(Goods.class));
    }

    @Test
    @DisplayName("普通用户不能修改他人商品")
    void cannotEditOthersGoods() {
        Goods g = new Goods();
        g.setId(100L);
        g.setUserId(2L);
        g.setStatus(Goods.STATUS_ON_SALE);
        when(goodsMapper.selectById(100L)).thenReturn(g);

        GoodsDTO dto = dto();
        dto.setId(100L);
        assertThatThrownBy(() -> service.update(dto, 9L))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("自己");
        verify(goodsMapper, never()).updateById(any(Goods.class));
    }

    @Test
    @DisplayName("管理员也不能通过普通接口改他人商品（必须走管理端接口）")
    void adminCannotUseNormalEditOnOthers() {
        Goods g = new Goods();
        g.setId(100L);
        g.setUserId(2L);
        g.setStatus(Goods.STATUS_ON_SALE);
        when(goodsMapper.selectById(100L)).thenReturn(g);

        GoodsDTO dto = dto();
        dto.setId(100L);
        assertThatThrownBy(() -> service.update(dto, 1L)) // 1 = 管理员，普通接口已不放行
                .isInstanceOf(BizException.class)
                .hasMessageContaining("自己");
        verify(goodsMapper, never()).updateById(any(Goods.class));
    }

    @Test
    @DisplayName("管理员专用接口可强制上下架任意商品")
    void adminForceChangeStatus() {
        Goods g = new Goods();
        g.setId(100L);
        g.setUserId(2L);
        g.setStatus(Goods.STATUS_LOCKED); // 普通接口下锁定商品禁止操作
        when(goodsMapper.selectById(100L)).thenReturn(g);

        service.adminForceChangeStatus(100L, Goods.STATUS_OFF);

        assertThat(g.getStatus()).isEqualTo(Goods.STATUS_OFF);
        verify(goodsMapper).updateById(g);
    }

    @Test
    @DisplayName("已锁定（有人下单未付款）的商品禁止删除")
    void cannotDeleteLockedGoods() {
        Goods g = new Goods();
        g.setId(100L);
        g.setUserId(2L);
        g.setStatus(Goods.STATUS_LOCKED);
        when(goodsMapper.selectById(100L)).thenReturn(g);

        assertThatThrownBy(() -> service.delete(100L, 2L))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("不能删除");
        verify(goodsMapper, never()).deleteById(anyLong());
    }

    @Test
    @DisplayName("上下架只接受 0/1，锁定商品禁止操作")
    void changeStatusGuards() {
        Goods g = new Goods();
        g.setId(100L);
        g.setUserId(2L);
        g.setStatus(Goods.STATUS_LOCKED);
        when(goodsMapper.selectById(100L)).thenReturn(g);

        assertThatThrownBy(() -> service.changeStatus(100L, 1, 2L))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("不能上下架");

        g.setStatus(Goods.STATUS_ON_SALE);
        assertThatThrownBy(() -> service.changeStatus(100L, 9, 2L))
                .isInstanceOf(BizException.class)
                .hasMessageContaining("只支持上架或下架");
    }
}
