package com.campus.trade.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.common.AdminOnly;
import com.campus.trade.common.Result;
import com.campus.trade.common.UserContext;
import com.campus.trade.entity.Goods;
import com.campus.trade.entity.Order;
import com.campus.trade.entity.User;
import com.campus.trade.mapper.GoodsMapper;
import com.campus.trade.mapper.OrderMapper;
import com.campus.trade.mapper.UserMapper;
import com.campus.trade.service.GoodsService;
import com.campus.trade.service.OrderService;
import com.campus.trade.service.UserService;
import com.campus.trade.vo.AdminStatsVO;
import com.campus.trade.vo.OrderVO;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

/**
 * 管理端接口。
 * <p>
 * 类上标了 @AdminOnly，JwtInterceptor 会对本类所有请求做 role=1 校验，
 * 所以这里的方法内部不用再写一遍权限判断。
 */
@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@AdminOnly
public class AdminController {

    private final UserService userService;
    private final GoodsService goodsService;
    private final OrderService orderService;
    private final UserMapper userMapper;
    private final GoodsMapper goodsMapper;
    private final OrderMapper orderMapper;

    /** 数据概览：GET /api/admin/stats */
    @GetMapping("/stats")
    public Result<AdminStatsVO> stats() {
        AdminStatsVO vo = new AdminStatsVO();
        vo.setUserCount(userMapper.selectCount(null));
        vo.setGoodsCount(goodsMapper.selectCount(null));
        vo.setOnSaleCount(goodsMapper.selectCount(
                new LambdaQueryWrapper<Goods>().eq(Goods::getStatus, Goods.STATUS_ON_SALE)));
        vo.setOrderCount(orderMapper.selectCount(null));
        vo.setFinishedCount(orderMapper.selectCount(
                new LambdaQueryWrapper<Order>().eq(Order::getStatus, Order.STATUS_FINISHED)));
        vo.setTodayOrderCount(orderMapper.selectCount(new LambdaQueryWrapper<Order>()
                .ge(Order::getCreateTime, LocalDate.now().atStartOfDay())));
        vo.setTradeAmount(sumTradeAmount());
        return Result.ok(vo);
    }

    /** 用户列表：GET /api/admin/users?pageNum=1&pageSize=10&keyword= */
    @GetMapping("/users")
    public Result<Page<User>> users(@RequestParam(defaultValue = "1") int pageNum,
                                    @RequestParam(defaultValue = "10") int pageSize,
                                    @RequestParam(required = false) String keyword) {
        return Result.ok(userService.adminPage(pageNum, pageSize, keyword));
    }

    /** 启用 / 禁用用户：PUT /api/admin/users/3/status?status=0 */
    @PutMapping("/users/{id}/status")
    public Result<Void> changeUserStatus(@PathVariable Long id, @RequestParam Integer status) {
        userService.changeStatus(id, status, UserContext.get());
        return Result.ok();
    }

    /** 全平台商品：GET /api/admin/goods?status=1&keyword= */
    @GetMapping("/goods")
    public Result<Page<Goods>> goods(@RequestParam(defaultValue = "1") int pageNum,
                                     @RequestParam(defaultValue = "10") int pageSize,
                                     @RequestParam(required = false) Integer status,
                                     @RequestParam(required = false) String keyword) {
        return Result.ok(goodsService.adminPage(pageNum, pageSize, status, keyword));
    }

    /**
     * 强制下架 / 恢复上架：PUT /api/admin/goods/5/status?status=0
     * 走管理员专用方法：不受"锁定商品不能上下架"限制，管理员可以强制处理违规商品。
     */
    @PutMapping("/goods/{id}/status")
    public Result<Void> changeGoodsStatus(@PathVariable Long id, @RequestParam Integer status) {
        goodsService.adminForceChangeStatus(id, status);
        return Result.ok();
    }

    /** 强制删除任意商品：DELETE /api/admin/goods/5（不受锁定状态限制） */
    @DeleteMapping("/goods/{id}")
    public Result<Void> deleteGoods(@PathVariable Long id) {
        goodsService.adminForceDelete(id);
        return Result.ok();
    }

    /** 全平台订单：GET /api/admin/orders?status=0&keyword=订单号 */
    @GetMapping("/orders")
    public Result<Page<OrderVO>> orders(@RequestParam(defaultValue = "1") int pageNum,
                                        @RequestParam(defaultValue = "10") int pageSize,
                                        @RequestParam(required = false) Integer status,
                                        @RequestParam(required = false) String keyword) {
        return Result.ok(orderService.adminPage(pageNum, pageSize, status, keyword));
    }

    /**
     * 累计成交额 = 已付款 + 已完成订单金额之和。
     * 用 SQL 的 SUM 而不是把订单全查出来在 Java 里加，数据量大了差距非常明显。
     */
    private BigDecimal sumTradeAmount() {
        List<Object> objs = orderMapper.selectObjs(new QueryWrapper<Order>()
                .select("IFNULL(SUM(amount), 0)")
                .in("status", Order.STATUS_PAID, Order.STATUS_FINISHED));
        if (objs == null || objs.isEmpty() || objs.get(0) == null) {
            return BigDecimal.ZERO;
        }
        return new BigDecimal(objs.get(0).toString());
    }
}
