package com.campus.trade.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.dto.OrderCreateDTO;
import com.campus.trade.vo.OrderVO;

public interface OrderService {

    /** 下单：把商品锁成"已锁定"，并生成待付款订单 */
    OrderVO create(OrderCreateDTO dto, Long buyerId);

    /**
     * 我的订单。
     * @param role buyer=我买到的，seller=我卖出的
     */
    Page<OrderVO> myPage(int pageNum, int pageSize, Integer status, String role, Long userId);

    /** 付款（模拟支付，没有接真实支付渠道） */
    void pay(Long orderId, Long userId);

    /** 确认收货，订单完成 */
    void finish(Long orderId, Long userId);

    /** 取消订单（未付款时买家或卖家都能取消），商品回到在售 */
    void cancel(Long orderId, Long userId, String reason);

    /** 管理员查看全平台订单 */
    Page<OrderVO> adminPage(int pageNum, int pageSize, Integer status, String keyword);

    /**
     * 取消超时未付款的订单，返回处理条数。
     * 由定时任务调用，防止商品被一个不付款的人长期锁死。
     */
    int cancelTimeoutOrders(int timeoutMinutes);
}
