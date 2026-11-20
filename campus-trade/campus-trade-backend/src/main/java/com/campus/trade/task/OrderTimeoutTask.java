package com.campus.trade.task;

import com.campus.trade.service.OrderService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 超时订单清理定时任务。
 * <p>
 * 为什么必须有这个：下单的瞬间商品会被锁成"已锁定"，如果买家下了单不付款，
 * 商品就永远卡在那里谁都买不了。所以要用定时任务把超过 2 小时没付款的订单自动取消，
 * 并把商品放回在售。
 * <p>
 * 用 fixedDelay 而不是 fixedRate：上一次跑完再等 5 分钟，避免任务堆积。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class OrderTimeoutTask {

    /** 付款时限（分钟）。答辩演示时可以临时改成 1 分钟，方便演示自动取消 */
    private static final int PAY_TIMEOUT_MINUTES = 120;

    private final OrderService orderService;

    @Scheduled(fixedDelay = 5 * 60 * 1000, initialDelay = 60 * 1000)
    public void cancelTimeoutOrders() {
        try {
            int count = orderService.cancelTimeoutOrders(PAY_TIMEOUT_MINUTES);
            if (count > 0) {
                log.info("定时任务：自动取消了 {} 个超过 {} 分钟未付款的订单", count, PAY_TIMEOUT_MINUTES);
            }
        } catch (Exception e) {
            // 定时任务里一定要吞异常，否则一次数据库抖动会让整个调度线程停掉
            log.error("超时订单清理失败", e);
        }
    }
}
