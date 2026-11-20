package com.campus.trade.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.dto.GoodsDTO;
import com.campus.trade.entity.Goods;
import com.campus.trade.vo.GoodsDetailVO;

public interface GoodsService {

    /** 分页查询在售商品，keyword/category 可为空 */
    Page<Goods> page(int pageNum, int pageSize, String keyword, String category);

    /**
     * 商品详情，带卖家信息。
     * @param currentUserId 当前登录人，用来判断"是不是我发布的"；可以为 null
     */
    GoodsDetailVO getDetail(Long id, Long currentUserId);

    /** 发布商品，返回新商品 id；状态由后端强制设为「在售」 */
    Long publish(GoodsDTO dto, Long userId);

    /** 编辑商品，只能改自己发布的（管理员走 adminForceChangeStatus，不经此口） */
    void update(GoodsDTO dto, Long userId);

    /** 我的发布：按状态筛选，status 为 null 查全部 */
    Page<Goods> myPage(int pageNum, int pageSize, Integer status, Long userId);

    /** 上架 / 下架，只接受 0 和 1 两个目标状态 */
    void changeStatus(Long id, Integer status, Long userId);

    /** 删除商品，只能删自己的（管理员除外） */
    void delete(Long id, Long userId);

    /**
     * 管理端：强制上下架任意商品。
     * 与普通 changeStatus 的区别：不受"锁定商品不能上下架"限制（管理员要能强制处理违规商品）。
     * 权限由 AdminController 类上的 @AdminOnly 保证，这里只做参数校验。
     */
    void adminForceChangeStatus(Long id, Integer status);

    /** 管理端：强制删除任意商品，同样不受锁定状态限制 */
    void adminForceDelete(Long id);

    /** 管理端：全平台商品，含已下架/已售出，可按状态和关键词筛选 */
    Page<Goods> adminPage(int pageNum, int pageSize, Integer status, String keyword);
}
