package com.campus.trade.service.impl;

import com.baomidou.mybatisplus.core.MybatisConfiguration;
import com.baomidou.mybatisplus.core.metadata.TableInfoHelper;
import com.campus.trade.entity.Goods;
import com.campus.trade.entity.Order;
import com.campus.trade.entity.User;
import org.apache.ibatis.builder.MapperBuilderAssistant;

/**
 * MyBatis-Plus Lambda 条件构造器在脱离 Spring 容器时，实体列缓存（LambdaUtils/TableInfo）不会被自动初始化，
 * 直接 new LambdaUpdateWrapper&lt;Goods&gt;().set(Goods::getStatus, ...) 会抛
 * "can not find lambda cache for this entity"。
 * 本工具在纯 Mockito 测试里手动预热缓存，让 Lambda 列引用可用。
 */
public final class LambdaCacheInit {

    private LambdaCacheInit() { }

    public static void init() {
        MapperBuilderAssistant assistant = new MapperBuilderAssistant(new MybatisConfiguration(), "unit-test");
        TableInfoHelper.initTableInfo(assistant, Goods.class);
        TableInfoHelper.initTableInfo(assistant, Order.class);
        TableInfoHelper.initTableInfo(assistant, User.class);
    }
}
