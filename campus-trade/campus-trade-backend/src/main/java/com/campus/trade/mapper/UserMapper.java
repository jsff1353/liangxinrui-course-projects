package com.campus.trade.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.campus.trade.entity.User;
import org.apache.ibatis.annotations.Mapper;

/**
 * 继承 BaseMapper 即拥有基础 CRUD，无需写 XML。
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {
}
