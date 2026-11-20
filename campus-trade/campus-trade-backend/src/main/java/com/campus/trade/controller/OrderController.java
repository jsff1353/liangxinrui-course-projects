package com.campus.trade.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.common.Result;
import com.campus.trade.common.UserContext;
import com.campus.trade.dto.OrderCreateDTO;
import com.campus.trade.service.OrderService;
import com.campus.trade.vo.OrderVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    /** 下单：POST /api/orders，body = { goodsId, remark } */
    @PostMapping
    public Result<OrderVO> create(@Valid @RequestBody OrderCreateDTO dto) {
        return Result.ok(orderService.create(dto, UserContext.get()));
    }

    /** 我的订单：GET /api/orders/my?role=buyer|seller&status=0 */
    @GetMapping("/my")
    public Result<Page<OrderVO>> my(@RequestParam(defaultValue = "1") int pageNum,
                                    @RequestParam(defaultValue = "5") int pageSize,
                                    @RequestParam(required = false) Integer status,
                                    @RequestParam(defaultValue = "buyer") String role) {
        return Result.ok(orderService.myPage(pageNum, pageSize, status, role, UserContext.get()));
    }

    /** 付款：PUT /api/orders/1/pay */
    @PutMapping("/{id}/pay")
    public Result<Void> pay(@PathVariable Long id) {
        orderService.pay(id, UserContext.get());
        return Result.ok();
    }

    /** 确认收货：PUT /api/orders/1/finish */
    @PutMapping("/{id}/finish")
    public Result<Void> finish(@PathVariable Long id) {
        orderService.finish(id, UserContext.get());
        return Result.ok();
    }

    /** 取消订单：PUT /api/orders/1/cancel?reason=不想要了 */
    @PutMapping("/{id}/cancel")
    public Result<Void> cancel(@PathVariable Long id,
                               @RequestParam(required = false) String reason) {
        orderService.cancel(id, UserContext.get(), reason);
        return Result.ok();
    }
}
