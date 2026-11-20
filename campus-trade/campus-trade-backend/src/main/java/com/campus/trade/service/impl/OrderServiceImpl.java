package com.campus.trade.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.common.BizException;
import com.campus.trade.dto.OrderCreateDTO;
import com.campus.trade.entity.Goods;
import com.campus.trade.entity.Order;
import com.campus.trade.entity.User;
import com.campus.trade.mapper.GoodsMapper;
import com.campus.trade.mapper.OrderMapper;
import com.campus.trade.mapper.UserMapper;
import com.campus.trade.service.OrderService;
import com.campus.trade.vo.OrderVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.Function;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {

    /** 精确到毫秒：14 位时间 + 3 位毫秒，比秒级大幅降低同刻并发的概率 */
    private static final DateTimeFormatter ORDER_NO_FMT = DateTimeFormatter.ofPattern("yyyyMMddHHmmssSSS");
    /** 进程内自增序列，保证同一毫秒内多个订单号也不重复 */
    private static final java.util.concurrent.atomic.AtomicLong ORDER_SEQ =
            new java.util.concurrent.atomic.AtomicLong(ThreadLocalRandom.current().nextInt(1000));

    private final OrderMapper orderMapper;
    private final GoodsMapper goodsMapper;
    private final UserMapper userMapper;

    /**
     * 下单。
     * <p>
     * 并发安全的关键在这一句：
     * <pre>
     * UPDATE goods SET status=2 WHERE id=? AND status=1
     * </pre>
     * 两个人同时点"立即购买"，数据库只会让一条 UPDATE 生效（行锁 + 条件判断是原子的），
     * 拿到 0 行就说明商品已经被别人抢走了。
     * 如果先 select 判断再 update，中间的时间差足够两个人都通过判断，就会生成两笔订单。
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public OrderVO create(OrderCreateDTO dto, Long buyerId) {
        Goods goods = goodsMapper.selectById(dto.getGoodsId());
        if (goods == null) {
            throw new BizException(404, "商品不存在或已删除");
        }
        if (buyerId.equals(goods.getUserId())) {
            throw new BizException("不能购买自己发布的商品");
        }
        if (goods.getStatus() == null || goods.getStatus() != Goods.STATUS_ON_SALE) {
            throw new BizException("商品当前不可购买（可能已下架、被锁定或已售出）");
        }

        // 抢占商品：只有"还是1在售"的情况才更新成功
        int locked = goodsMapper.update(null, new LambdaUpdateWrapper<Goods>()
                .set(Goods::getStatus, Goods.STATUS_LOCKED)
                .set(Goods::getUpdateTime, LocalDateTime.now())
                .eq(Goods::getId, goods.getId())
                .eq(Goods::getStatus, Goods.STATUS_ON_SALE));
        if (locked == 0) {
            throw new BizException("手慢了，商品刚被别人下单");
        }

        Order order = new Order();
        order.setOrderNo(generateOrderNo());
        order.setBuyerId(buyerId);
        order.setSellerId(goods.getUserId());
        order.setGoodsId(goods.getId());
        // 金额与商品信息快照：卖家改价、下架甚至删除商品后，这笔订单仍保留原始成交信息
        order.setAmount(goods.getPrice());
        order.setGoodsTitleSnapshot(goods.getTitle());
        order.setGoodsCoverSnapshot(goods.getCoverImg());
        order.setGoodsCategorySnapshot(goods.getCategory());
        order.setRemark(dto.getRemark());
        order.setStatus(Order.STATUS_UNPAID);
        orderMapper.insert(order);

        log.info("创建订单 buyer={} goods={} orderNo={}", buyerId, goods.getId(), order.getOrderNo());
        return toVO(order, goods, null, null);
    }

    @Override
    public Page<OrderVO> myPage(int pageNum, int pageSize, Integer status, String role, Long userId) {
        boolean asSeller = "seller".equalsIgnoreCase(role);
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(asSeller ? Order::getSellerId : Order::getBuyerId, userId)
                .eq(status != null, Order::getStatus, status)
                .orderByDesc(Order::getCreateTime);
        return convert(orderMapper.selectPage(new Page<>(pageNum, pageSize), wrapper));
    }

    /**
     * 付款。状态更新同样用"条件 UPDATE"而不是先查后改：
     * 连点两下付款按钮时，第二次会拿到 0 行，直接提示状态已变更，不会重复写入付款时间。
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void pay(Long orderId, Long userId) {
        Order order = getById(orderId);
        if (!userId.equals(order.getBuyerId())) {
            throw new BizException(403, "只有买家可以付款");
        }
        int rows = orderMapper.update(null, new LambdaUpdateWrapper<Order>()
                .set(Order::getStatus, Order.STATUS_PAID)
                .set(Order::getPayTime, LocalDateTime.now())
                .eq(Order::getId, orderId)
                .eq(Order::getStatus, Order.STATUS_UNPAID));
        if (rows == 0) {
            throw new BizException("订单状态已变更，请刷新后重试");
        }

        // 付款后商品彻底卖出，不再出现在列表里
        goodsMapper.update(null, new LambdaUpdateWrapper<Goods>()
                .set(Goods::getStatus, Goods.STATUS_SOLD)
                .set(Goods::getUpdateTime, LocalDateTime.now())
                .eq(Goods::getId, order.getGoodsId()));
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void finish(Long orderId, Long userId) {
        Order order = getById(orderId);
        if (!userId.equals(order.getBuyerId())) {
            throw new BizException(403, "只有买家可以确认收货");
        }
        int rows = orderMapper.update(null, new LambdaUpdateWrapper<Order>()
                .set(Order::getStatus, Order.STATUS_FINISHED)
                .set(Order::getFinishTime, LocalDateTime.now())
                .eq(Order::getId, orderId)
                .eq(Order::getStatus, Order.STATUS_PAID));
        if (rows == 0) {
            throw new BizException("只有已付款的订单才能确认收货");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void cancel(Long orderId, Long userId, String reason) {
        Order order = getById(orderId);
        // 买家和卖家都能取消，但第三方不行
        if (!userId.equals(order.getBuyerId()) && !userId.equals(order.getSellerId())) {
            throw new BizException(403, "无权操作该订单");
        }
        int rows = orderMapper.update(null, new LambdaUpdateWrapper<Order>()
                .set(Order::getStatus, Order.STATUS_CANCELED)
                .set(Order::getCancelReason,
                        StringUtils.hasText(reason) ? reason : "用户主动取消")
                .eq(Order::getId, orderId)
                .eq(Order::getStatus, Order.STATUS_UNPAID));
        if (rows == 0) {
            throw new BizException("只有未付款的订单可以取消，已付款请联系卖家协商");
        }
        releaseGoods(order.getGoodsId());
    }

    @Override
    public Page<OrderVO> adminPage(int pageNum, int pageSize, Integer status, String keyword) {
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(status != null, Order::getStatus, status);

        if (StringUtils.hasText(keyword)) {
            // 管理员搜索框可能填订单号，也可能填商品名，两种都支持：
            // 先用商品名查出商品 id，再让订单去匹配 order_no 或 goods_id
            List<Long> goodsIds = goodsMapper
                    .selectObjs(new QueryWrapper<Goods>().select("id").like("title", keyword))
                    .stream()
                    .filter(java.util.Objects::nonNull)
                    .map(o -> Long.valueOf(o.toString()))
                    .collect(Collectors.toList());
            wrapper.and(w -> {
                w.like(Order::getOrderNo, keyword);
                if (!goodsIds.isEmpty()) {
                    w.or().in(Order::getGoodsId, goodsIds);
                }
            });
        }

        wrapper.orderByDesc(Order::getCreateTime);
        return convert(orderMapper.selectPage(new Page<>(pageNum, pageSize), wrapper));
    }

    /**
     * 定时任务专用：这里刻意不加 @Transactional。
     * 一批订单放在一个大事务里，一旦某条失败会全部回滚，而超时取消本身是"能做多少做多少"的任务。
     */
    @Override
    public int cancelTimeoutOrders(int timeoutMinutes) {
        LocalDateTime deadline = LocalDateTime.now().minusMinutes(timeoutMinutes);
        List<Order> timeoutList = orderMapper.selectList(new LambdaQueryWrapper<Order>()
                .eq(Order::getStatus, Order.STATUS_UNPAID)
                .lt(Order::getCreateTime, deadline));

        int count = 0;
        for (Order order : timeoutList) {
            int rows = orderMapper.update(null, new LambdaUpdateWrapper<Order>()
                    .set(Order::getStatus, Order.STATUS_CANCELED)
                    .set(Order::getCancelReason, "超过 " + timeoutMinutes + " 分钟未付款，系统自动取消")
                    .eq(Order::getId, order.getId())
                    .eq(Order::getStatus, Order.STATUS_UNPAID));
            if (rows > 0) {
                releaseGoods(order.getGoodsId());
                count++;
            }
        }
        return count;
    }

    // ---------------------------------------------------------------
    // 私有工具方法
    // ---------------------------------------------------------------

    private Order getById(Long orderId) {
        if (orderId == null) {
            throw new BizException("缺少订单ID");
        }
        Order order = orderMapper.selectById(orderId);
        if (order == null) {
            throw new BizException(404, "订单不存在");
        }
        return order;
    }

    /** 订单作废后把商品放回在售（只有"已锁定"才改，已售出的不受影响） */
    private void releaseGoods(Long goodsId) {
        goodsMapper.update(null, new LambdaUpdateWrapper<Goods>()
                .set(Goods::getStatus, Goods.STATUS_ON_SALE)
                .set(Goods::getUpdateTime, LocalDateTime.now())
                .eq(Goods::getId, goodsId)
                .eq(Goods::getStatus, Goods.STATUS_LOCKED));
    }

    /**
     * 订单号 = 17 位毫秒时间 + 4 位进程内自增序列 + 2 位随机数。
     * <p>
     * 原来是"秒级时间 + 6 位随机"，同一秒内碰撞概率不够低，撞上唯一索引 uk_order_no 会报
     * DuplicateKeyException（用户看到"数据已存在，请勿重复提交"，很莫名）。
     * 现在毫秒时间 + AtomicLong 自增保证单实例绝不重复，末尾随机数降低多实例部署的碰撞面，
     * 数据库唯一索引仍作为最后兜底。
     * 不用数据库自增 ID 当订单号，是避免把"这周成交多少单"这类经营数据暴露出去。
     */
    private String generateOrderNo() {
        long seq = ORDER_SEQ.incrementAndGet() % 10_000;
        int rand = ThreadLocalRandom.current().nextInt(100);
        return LocalDateTime.now().format(ORDER_NO_FMT)
                + String.format("%04d%02d", seq, rand);
    }

    /**
     * 分页结果 -> VO。
     * 用 selectBatchIds 一次性把商品和用户查回来，避免在循环里查库（N+1 查询）。
     */
    private Page<OrderVO> convert(Page<Order> page) {
        Page<OrderVO> result = new Page<>(page.getCurrent(), page.getSize(), page.getTotal());
        List<Order> records = page.getRecords();
        if (records.isEmpty()) {
            result.setRecords(Collections.emptyList());
            return result;
        }

        Set<Long> goodsIds = records.stream().map(Order::getGoodsId).collect(Collectors.toSet());
        Set<Long> userIds = records.stream()
                .flatMap(o -> java.util.stream.Stream.of(o.getBuyerId(), o.getSellerId()))
                .collect(Collectors.toSet());

        Map<Long, Goods> goodsMap = goodsIds.isEmpty()
                ? Collections.emptyMap()
                : goodsMapper.selectBatchIds(goodsIds).stream()
                .collect(Collectors.toMap(Goods::getId, Function.identity()));
        Map<Long, User> userMap = userIds.isEmpty()
                ? Collections.emptyMap()
                : userMapper.selectBatchIds(userIds).stream()
                .collect(Collectors.toMap(User::getId, Function.identity()));

        List<OrderVO> voList = records.stream()
                .map(o -> toVO(o, goodsMap.get(o.getGoodsId()),
                        userMap.get(o.getBuyerId()), userMap.get(o.getSellerId())))
                .collect(Collectors.toList());
        result.setRecords(voList);
        return result;
    }

    private OrderVO toVO(Order order, Goods goods, User buyer, User seller) {
        OrderVO vo = new OrderVO();
        vo.setId(order.getId());
        vo.setOrderNo(order.getOrderNo());
        vo.setBuyerId(order.getBuyerId());
        vo.setSellerId(order.getSellerId());
        vo.setGoodsId(order.getGoodsId());
        vo.setAmount(order.getAmount());
        vo.setRemark(order.getRemark());
        vo.setStatus(order.getStatus());
        vo.setPayTime(order.getPayTime());
        vo.setFinishTime(order.getFinishTime());
        vo.setCancelReason(order.getCancelReason());
        vo.setCreateTime(order.getCreateTime());
        vo.setUpdateTime(order.getUpdateTime());

        if (goods != null) {
            vo.setGoodsTitle(goods.getTitle());
            vo.setGoodsCover(goods.getCoverImg());
            vo.setGoodsCategory(goods.getCategory());
        } else {
            // 商品已被物理删除：用下单时的快照兜底，订单列表不至于显示空白
            vo.setGoodsTitle(order.getGoodsTitleSnapshot());
            vo.setGoodsCover(order.getGoodsCoverSnapshot());
            vo.setGoodsCategory(order.getGoodsCategorySnapshot());
        }
        if (buyer != null) {
            vo.setBuyerNickname(buyer.getNickname());
        }
        if (seller != null) {
            vo.setSellerNickname(seller.getNickname());
        }
        return vo;
    }
}
