package com.campus.trade.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.common.Result;
import com.campus.trade.common.UserContext;
import com.campus.trade.dto.GoodsDTO;
import com.campus.trade.entity.Goods;
import com.campus.trade.service.GoodsService;
import com.campus.trade.vo.GoodsDetailVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/goods")
@RequiredArgsConstructor
public class GoodsController {

    private final GoodsService goodsService;

    /** 商品分页列表：GET /api/goods/page?pageNum=1&pageSize=8&keyword=&category= */
    @GetMapping("/page")
    public Result<Page<Goods>> page(@RequestParam(defaultValue = "1") int pageNum,
                                    @RequestParam(defaultValue = "8") int pageSize,
                                    @RequestParam(required = false) String keyword,
                                    @RequestParam(required = false) String category) {
        return Result.ok(goodsService.page(pageNum, pageSize, keyword, category));
    }

    /** 我的发布：GET /api/goods/my?status=1 */
    @GetMapping("/my")
    public Result<Page<Goods>> my(@RequestParam(defaultValue = "1") int pageNum,
                                  @RequestParam(defaultValue = "8") int pageSize,
                                  @RequestParam(required = false) Integer status) {
        return Result.ok(goodsService.myPage(pageNum, pageSize, status, UserContext.get()));
    }

    /** 发布商品：POST /api/goods，发布者取自 token，前端传的 userId 一律无效 */
    @PostMapping
    public Result<Long> publish(@Valid @RequestBody GoodsDTO dto) {
        return Result.ok(goodsService.publish(dto, UserContext.get()));
    }

    /** 编辑商品：PUT /api/goods/1 */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @Valid @RequestBody GoodsDTO dto) {
        dto.setId(id);
        goodsService.update(dto, UserContext.get());
        return Result.ok();
    }

    /** 上架 / 下架：PUT /api/goods/1/status?status=0 */
    @PutMapping("/{id}/status")
    public Result<Void> changeStatus(@PathVariable Long id, @RequestParam Integer status) {
        goodsService.changeStatus(id, status, UserContext.get());
        return Result.ok();
    }

    /** 删除商品：DELETE /api/goods/1 */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        goodsService.delete(id, UserContext.get());
        return Result.ok();
    }

    /** 商品详情：GET /api/goods/1，附带卖家信息和"是否我发布的" */
    @GetMapping("/{id}")
    public Result<GoodsDetailVO> detail(@PathVariable Long id) {
        return Result.ok(goodsService.getDetail(id, UserContext.get()));
    }
}
