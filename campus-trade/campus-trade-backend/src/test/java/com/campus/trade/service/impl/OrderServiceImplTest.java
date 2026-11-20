package com.campus.trade.service.impl;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.campus.trade.common.BizException;
import com.campus.trade.dto.OrderCreateDTO;
import com.campus.trade.entity.Goods;
import com.campus.trade.entity.Order;
import com.campus.trade.entity.User;
import com.campus.trade.mapper.GoodsMapper;
import com.campus.trade.mapper.OrderMapper;
import com.campus.trade.mapper.UserMapper;
import com.campus.trade.vo.OrderVO;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * 订单服务单元测试：覆盖状态机、并发锁定、金额快照、越权校验、超时取消。
 * 纯 Mockito，不连数据库，答辩现场无 MySQL 也能跑。
 */
@ExtendWith(MockitoExtension.class)
class OrderServiceImplTest {

    @Mock private OrderMapper orderMapper;
    @Mock private GoodsMapper goodsMapper;
    @Mock private UserMapper userMapper;

    private OrderServiceImpl service;

    @BeforeAll
    static void initLambdaCache() {
        LambdaCacheInit.init();
    }

    @BeforeEach
    void setUp() {
        service = new OrderServiceImpl(orderMapper, goodsMapper, userMapper);
    }

    private Goods onSaleGoods() {
        Goods g = new Goods();
        g.setId(100L);
        g.setUserId(2L);           // 卖家
        g.setTitle("高等数学上册");
        g.setPrice(new BigDecimal("15.00"));
        g.setCategory("教材");
        g.setCoverImg("/uploads/a.jpg");
        g.setStatus(Goods.STATUS_ON_SALE);
        return g;
    }

    private OrderCreateDTO dto(Long goodsId) {
        OrderCreateDTO dto = new OrderCreateDTO();
        dto.setGoodsId(goodsId);
        dto.setRemark("宿舍楼下交易");
        return dto;
    }

    @Nested
    @DisplayName("下单 create")
    class CreateTest {

        @Test
        @DisplayName("正常下单：锁定商品、生成待付款订单、金额取自商品而非前端")
        void createSuccess() {
            when(goodsMapper.selectById(100L)).thenReturn(onSaleGoods());
            when(goodsMapper.update(isNull(), any(Wrapper.class))).thenReturn(1);

            OrderVO vo = service.create(dto(100L), 3L); // 买家 id=3

            ArgumentCaptor<Order> orderCap = ArgumentCaptor.forClass(Order.class);
            verify(orderMapper).insert(orderCap.capture());
            Order saved = orderCap.getValue();
            assertThat(saved.getBuyerId()).isEqualTo(3L);
            assertThat(saved.getSellerId()).isEqualTo(2L);
            assertThat(saved.getGoodsId()).isEqualTo(100L);
            assertThat(saved.getAmount()).isEqualByComparingTo("15.00");
            assertThat(saved.getGoodsTitleSnapshot()).isEqualTo("高等数学上册");
            assertThat(saved.getGoodsCategorySnapshot()).isEqualTo("教材");
            assertThat(saved.getStatus()).isEqualTo(Order.STATUS_UNPAID);
            assertThat(saved.getOrderNo()).hasSize(23); // 17 位毫秒时间 + 4 位序列 + 2 位随机

            // 关键：锁定走的是带 status 条件的更新，而不是先查后改
            ArgumentCaptor<Wrapper> wrapperCap = ArgumentCaptor.forClass(Wrapper.class);
            verify(goodsMapper).update(isNull(), wrapperCap.capture());
            assertThat(wrapperCap.getValue().getSqlSegment()).contains("status");

            assertThat(vo.getStatus()).isEqualTo(Order.STATUS_UNPAID);
        }

        @Test
        @DisplayName("不能购买自己发布的商品")
        void cannotBuyOwnGoods() {
            Goods g = onSaleGoods();
            g.setUserId(3L); // 买家就是卖家
            when(goodsMapper.selectById(100L)).thenReturn(g);

            assertThatThrownBy(() -> service.create(dto(100L), 3L))
                    .isInstanceOf(BizException.class)
                    .hasMessageContaining("自己");

            verify(orderMapper, never()).insert(any(Order.class));
        }

        @Test
        @DisplayName("商品非在售状态不可下单")
        void goodsNotOnSale() {
            Goods g = onSaleGoods();
            g.setStatus(Goods.STATUS_SOLD);
            when(goodsMapper.selectById(100L)).thenReturn(g);

            assertThatThrownBy(() -> service.create(dto(100L), 3L))
                    .isInstanceOf(BizException.class)
                    .hasMessageContaining("不可购买");
        }

        @Test
        @DisplayName("并发抢购：条件更新返回 0 时不生成订单（防超卖核心）")
        void lockFailedNoOrder() {
            when(goodsMapper.selectById(100L)).thenReturn(onSaleGoods());
            when(goodsMapper.update(isNull(), any(Wrapper.class))).thenReturn(0); // 被别人抢先

            assertThatThrownBy(() -> service.create(dto(100L), 3L))
                    .isInstanceOf(BizException.class)
                    .hasMessageContaining("手慢了");

            verify(orderMapper, never()).insert(any(Order.class));
        }

        @Test
        @DisplayName("商品不存在时下单失败")
        void goodsNotFound() {
            when(goodsMapper.selectById(999L)).thenReturn(null);
            assertThatThrownBy(() -> service.create(dto(999L), 3L))
                    .isInstanceOf(BizException.class)
                    .hasMessageContaining("不存在");
        }
    }

    @Nested
    @DisplayName("支付与完成 pay/finish")
    class PayTest {

        private Order unpaidOrder() {
            Order o = new Order();
            o.setId(1L);
            o.setBuyerId(3L);
            o.setGoodsId(100L);
            o.setStatus(Order.STATUS_UNPAID);
            return o;
        }

        @Test
        @DisplayName("付款成功：订单转已付款，商品转已售出")
        void paySuccess() {
            when(orderMapper.selectById(1L)).thenReturn(unpaidOrder());
            when(orderMapper.update(isNull(), any(Wrapper.class))).thenReturn(1);

            service.pay(1L, 3L);

            verify(orderMapper).update(isNull(), any(Wrapper.class));
            verify(goodsMapper).update(isNull(), any(Wrapper.class));
        }

        @Test
        @DisplayName("只有买家能付款")
        void payByNonBuyer() {
            when(orderMapper.selectById(1L)).thenReturn(unpaidOrder());
            assertThatThrownBy(() -> service.pay(1L, 99L))
                    .isInstanceOf(BizException.class)
                    .hasMessageContaining("只有买家");
            verify(orderMapper, never()).update(any(), any());
        }

        @Test
        @DisplayName("重复付款：条件更新返回 0，不重复把商品置为售出")
        void repeatedPayBlocked() {
            when(orderMapper.selectById(1L)).thenReturn(unpaidOrder());
            when(orderMapper.update(isNull(), any(Wrapper.class))).thenReturn(0);

            assertThatThrownBy(() -> service.pay(1L, 3L))
                    .isInstanceOf(BizException.class)
                    .hasMessageContaining("状态已变更");

            verify(goodsMapper, never()).update(any(), any());
        }

        @Test
        @DisplayName("只有已付款订单能确认收货")
        void finishRequiresPaid() {
            Order o = unpaidOrder();
            when(orderMapper.selectById(1L)).thenReturn(o);
            when(orderMapper.update(isNull(), any(Wrapper.class))).thenReturn(0);

            assertThatThrownBy(() -> service.finish(1L, 3L))
                    .isInstanceOf(BizException.class)
                    .hasMessageContaining("已付款");
        }
    }

    @Nested
    @DisplayName("取消与超时 cancel")
    class CancelTest {

        @Test
        @DisplayName("买家取消未付款订单后释放商品回在售")
        void cancelReleasesGoods() {
            Order o = new Order();
            o.setId(1L);
            o.setBuyerId(3L);
            o.setSellerId(2L);
            o.setGoodsId(100L);
            o.setStatus(Order.STATUS_UNPAID);
            when(orderMapper.selectById(1L)).thenReturn(o);
            when(orderMapper.update(isNull(), any(Wrapper.class))).thenReturn(1);

            service.cancel(1L, 3L, "不想要了");

            verify(goodsMapper).update(isNull(), any(Wrapper.class));
        }

        @Test
        @DisplayName("第三方无权取消订单")
        void cancelByStranger() {
            Order o = new Order();
            o.setId(1L);
            o.setBuyerId(3L);
            o.setSellerId(2L);
            o.setStatus(Order.STATUS_UNPAID);
            when(orderMapper.selectById(1L)).thenReturn(o);

            assertThatThrownBy(() -> service.cancel(1L, 99L, ""))
                    .isInstanceOf(BizException.class)
                    .hasMessageContaining("无权");
            verify(goodsMapper, never()).update(any(), any());
        }

        @Test
        @DisplayName("超时任务：只取消超时未付款订单并释放对应商品")
        void cancelTimeoutOrders() {
            Order o = new Order();
            o.setId(1L);
            o.setGoodsId(100L);
            o.setStatus(Order.STATUS_UNPAID);
            o.setCreateTime(LocalDateTime.now().minusHours(3));
            when(orderMapper.selectList(any(Wrapper.class))).thenReturn(List.of(o));
            when(orderMapper.update(isNull(), any(Wrapper.class))).thenReturn(1);

            int count = service.cancelTimeoutOrders(120);

            assertThat(count).isEqualTo(1);
            verify(goodsMapper).update(isNull(), any(Wrapper.class));
        }

        @Test
        @DisplayName("超时任务：并发下已被付款的订单不会被误取消")
        void cancelTimeoutSkipsAlreadyPaid() {
            Order o = new Order();
            o.setId(1L);
            o.setGoodsId(100L);
            o.setStatus(Order.STATUS_UNPAID);
            when(orderMapper.selectList(any(Wrapper.class))).thenReturn(List.of(o));
            when(orderMapper.update(isNull(), any(Wrapper.class))).thenReturn(0); // 已被并发改掉

            int count = service.cancelTimeoutOrders(120);

            assertThat(count).isZero();
            verify(goodsMapper, never()).update(any(), any());
        }
    }

    @Nested
    @DisplayName("订单商品快照")
    class SnapshotTest {

        @Test
        @DisplayName("商品被删除后，订单列表仍显示下单时的商品标题/分类")
        void showsSnapshotWhenGoodsDeleted() {
            Order o = new Order();
            o.setId(1L);
            o.setBuyerId(3L);
            o.setGoodsId(100L);
            o.setStatus(Order.STATUS_FINISHED);
            o.setGoodsTitleSnapshot("高等数学上册");
            o.setGoodsCategorySnapshot("教材");
            com.baomidou.mybatisplus.extension.plugins.pagination.Page<Order> page =
                    new com.baomidou.mybatisplus.extension.plugins.pagination.Page<>(1, 10);
            page.setRecords(List.of(o));
            page.setTotal(1);
            when(orderMapper.selectPage(any(), any(Wrapper.class))).thenReturn(page);
            // 商品已被删除：两个批量查询都返回空
            when(goodsMapper.selectBatchIds(any())).thenReturn(List.of());
            when(userMapper.selectBatchIds(any())).thenReturn(List.of());

            com.baomidou.mybatisplus.extension.plugins.pagination.Page<OrderVO> result =
                    service.myPage(1, 10, null, "buyer", 3L);

            OrderVO vo = result.getRecords().get(0);
            assertThat(vo.getGoodsTitle()).isEqualTo("高等数学上册");
            assertThat(vo.getGoodsCategory()).isEqualTo("教材");
        }
    }
}
