package com.campus.trade.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.trade.common.BizException;
import com.campus.trade.dto.GoodsDTO;
import com.campus.trade.entity.Goods;
import com.campus.trade.entity.Order;
import com.campus.trade.entity.User;
import com.campus.trade.mapper.GoodsMapper;
import com.campus.trade.mapper.OrderMapper;
import com.campus.trade.mapper.UserMapper;
import com.campus.trade.service.GoodsService;
import com.campus.trade.vo.GoodsDetailVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
@RequiredArgsConstructor
public class GoodsServiceImpl implements GoodsService {

    private final GoodsMapper goodsMapper;
    private final UserMapper userMapper;
    private final OrderMapper orderMapper;

    @Override
    public Page<Goods> page(int pageNum, int pageSize, String keyword, String category) {
        LambdaQueryWrapper<Goods> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Goods::getStatus, Goods.STATUS_ON_SALE) // 只查在售
                .like(StringUtils.hasText(keyword), Goods::getTitle, keyword)
                .eq(StringUtils.hasText(category), Goods::getCategory, category)
                .orderByDesc(Goods::getCreateTime);
        return goodsMapper.selectPage(new Page<>(pageNum, pageSize), wrapper);
    }

    @Override
    public GoodsDetailVO getDetail(Long id, Long currentUserId) {
        Goods goods = goodsMapper.selectById(id);
        if (goods == null) {
            throw new BizException(404, "商品不存在或已删除");
        }

        // 浏览量 +1 交给数据库做（view_count = view_count + 1），
        // 不能先查出来再 set 再 update，并发下会互相覆盖导致少计数
        goodsMapper.update(null, new LambdaUpdateWrapper<Goods>()
                .setSql("view_count = view_count + 1")
                .eq(Goods::getId, id));
        goods.setViewCount((goods.getViewCount() == null ? 0 : goods.getViewCount()) + 1);

        GoodsDetailVO vo = new GoodsDetailVO();
        org.springframework.beans.BeanUtils.copyProperties(goods, vo);

        User seller = userMapper.selectById(goods.getUserId());
        if (seller != null) {
            vo.setSellerNickname(seller.getNickname());
            vo.setSellerAvatar(seller.getAvatar());
            vo.setSellerCampus(seller.getCampus());
        }
        vo.setMine(currentUserId != null && currentUserId.equals(goods.getUserId()));

        // 该商品是否有进行中的订单（待付款/已付款），前端据此把按钮换成"去我的订单"
        Order active = orderMapper.selectOne(new LambdaQueryWrapper<Order>()
                .eq(Order::getGoodsId, id)
                .in(Order::getStatus, Order.STATUS_UNPAID, Order.STATUS_PAID)
                .orderByDesc(Order::getId)
                .last("LIMIT 1"));
        vo.setActiveOrderId(active == null ? null : active.getId());

        return vo;
    }

    @Override
    @Transactional
    public Long publish(GoodsDTO dto, Long userId) {
        checkPrice(dto);

        Goods goods = new Goods();
        copy(dto, goods);
        goods.setUserId(userId);
        // 状态和浏览量由后端决定，前端传什么都不采用
        goods.setStatus(Goods.STATUS_ON_SALE);
        goods.setViewCount(0);
        goodsMapper.insert(goods);
        return goods.getId();
    }

    @Override
    @Transactional
    public void update(GoodsDTO dto, Long userId) {
        Goods old = getOwned(dto.getId(), userId, "只能修改自己发布的商品");
        if (old.getStatus() == Goods.STATUS_LOCKED) {
            throw new BizException("商品已有买家下单未付款，暂时不能修改");
        }
        checkPrice(dto);

        copy(dto, old);
        goodsMapper.updateById(old);
    }

    @Override
    public Page<Goods> myPage(int pageNum, int pageSize, Integer status, Long userId) {
        LambdaQueryWrapper<Goods> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Goods::getUserId, userId)
                .eq(status != null, Goods::getStatus, status)
                .orderByDesc(Goods::getCreateTime);
        return goodsMapper.selectPage(new Page<>(pageNum, pageSize), wrapper);
    }

    @Override
    public Page<Goods> adminPage(int pageNum, int pageSize, Integer status, String keyword) {
        LambdaQueryWrapper<Goods> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(status != null, Goods::getStatus, status)
                .like(StringUtils.hasText(keyword), Goods::getTitle, keyword)
                .orderByDesc(Goods::getCreateTime);
        return goodsMapper.selectPage(new Page<>(pageNum, pageSize), wrapper);
    }

    @Override
    public void changeStatus(Long id, Integer status, Long userId) {
        Goods goods = getOwned(id, userId, "只能操作自己发布的商品");
        if (status == null || (status != Goods.STATUS_OFF && status != Goods.STATUS_ON_SALE)) {
            throw new BizException("只支持上架或下架操作");
        }
        if (goods.getStatus() == Goods.STATUS_LOCKED) {
            throw new BizException("商品有未完成的订单，不能上下架");
        }
        goods.setStatus(status);
        goodsMapper.updateById(goods);
    }

    @Override
    public void delete(Long id, Long userId) {
        Goods goods = getOwned(id, userId, "只能删除自己发布的商品");
        if (goods.getStatus() == Goods.STATUS_LOCKED) {
            throw new BizException("商品有未完成的订单，不能删除");
        }
        goodsMapper.deleteById(id);
    }

    @Override
    public void adminForceChangeStatus(Long id, Integer status) {
        if (id == null) {
            throw new BizException("缺少商品ID");
        }
        if (status == null || (status != Goods.STATUS_OFF && status != Goods.STATUS_ON_SALE)) {
            throw new BizException("只支持上架或下架操作");
        }
        Goods goods = goodsMapper.selectById(id);
        if (goods == null) {
            throw new BizException(404, "商品不存在或已删除");
        }
        goods.setStatus(status);
        goodsMapper.updateById(goods);
    }

    @Override
    public void adminForceDelete(Long id) {
        if (id == null) {
            throw new BizException("缺少商品ID");
        }
        if (goodsMapper.selectById(id) == null) {
            throw new BizException(404, "商品不存在或已删除");
        }
        goodsMapper.deleteById(id);
    }

    // ---------------------------------------------------------------
    // 私有工具方法
    // ---------------------------------------------------------------

    /**
     * 查商品并校验归属：只有发布者本人能操作。
     * <p>
     * 之前这里对 role=1 放行，导致管理员通过普通接口 PUT /api/goods/{id} 就能改任意商品（含价格），
     * 绕开了管理端接口的设计边界。现在普通接口严格只认本人；管理员的强制操作统一走
     * {@link #adminForceChangeStatus} / {@link #adminForceDelete}，由 AdminController 的 @AdminOnly 把关。
     * 越权校验必须在后端做，前端把按钮藏起来只是"看不见"，拦不住直接调接口的人。
     */
    private Goods getOwned(Long id, Long userId, String denyMsg) {
        if (id == null) {
            throw new BizException("缺少商品ID");
        }
        Goods goods = goodsMapper.selectById(id);
        if (goods == null) {
            throw new BizException(404, "商品不存在或已删除");
        }
        if (userId != null && userId.equals(goods.getUserId())) {
            return goods;
        }
        throw new BizException(403, denyMsg);
    }

    private void checkPrice(GoodsDTO dto) {
        if (dto.getOriginalPrice() != null
                && dto.getPrice() != null
                && dto.getOriginalPrice().compareTo(dto.getPrice()) < 0) {
            throw new BizException("原价不能低于售价");
        }
    }

    private void copy(GoodsDTO dto, Goods goods) {
        goods.setTitle(dto.getTitle() == null ? null : dto.getTitle().trim());
        goods.setDescription(dto.getDescription());
        goods.setPrice(dto.getPrice());
        goods.setOriginalPrice(dto.getOriginalPrice());
        goods.setCategory(dto.getCategory());
        goods.setItemCondition(dto.getItemCondition());
        goods.setTradePlace(dto.getTradePlace());
        goods.setContact(dto.getContact());
        goods.setCoverImg(dto.getCoverImg());
    }
}
