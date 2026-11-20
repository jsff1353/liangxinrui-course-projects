package com.campus.trade.service.impl;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.campus.trade.config.AiProperties;
import com.campus.trade.entity.Goods;
import com.campus.trade.mapper.GoodsMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.client.RestTemplate;

import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * AI 事实核对测试：重点验证"顿号误伤"已修复——
 * 正常的口语分句不再被整段替换，只有库里核不上的商品名/价格才兜底。
 * guardFacts 是私有方法，用反射直接调用，不依赖真实大模型。
 */
@ExtendWith(MockitoExtension.class)
class AiServiceImplTest {

    @Mock private AiProperties properties;
    @Mock private RestTemplate aiRestTemplate;
    @Mock private GoodsMapper goodsMapper;

    private AiServiceImpl service;
    private Method guardFacts;

    @BeforeAll
    static void init() {
        LambdaCacheInit.init();
    }

    @BeforeEach
    void setUp() throws Exception {
        service = new AiServiceImpl(properties, aiRestTemplate, new ObjectMapper(), goodsMapper);
        guardFacts = AiServiceImpl.class.getDeclaredMethod("guardFacts", String.class, List.class);
        guardFacts.setAccessible(true);
    }

    private Goods goods(String title, String price, int condition) {
        Goods g = new Goods();
        g.setTitle(title);
        g.setPrice(new BigDecimal(price));
        g.setItemCondition(condition);
        g.setCategory("教材");
        return g;
    }

    private String guard(String reply, List<Goods> goods) throws Exception {
        return (String) guardFacts.invoke(service, reply, goods);
    }

    @Test
    @DisplayName("正常顿号分句（价格实惠、成色不错）不再被误伤成数据库摘要")
    void keepsNaturalPunctuation() throws Exception {
        List<Goods> goods = List.of(goods("高等数学上册 同济第七版", "15.00", 2));
        String reply = "这本高等数学上册挺划算的，价格实惠、成色不错，校内当面交易。";

        String result = guard(reply, goods);

        assertThat(result).isEqualTo(reply); // 原样保留
    }

    @Test
    @DisplayName("顿号列举的真实商品名不被替换")
    void keepsRealProductNames() throws Exception {
        List<Goods> goods = List.of(
                goods("高等数学上册 同济第七版", "15.00", 2),
                goods("线性代数 同济第六版", "12.00", 1));
        String reply = "有高等数学上册、线性代数，都在教材分类里。";

        String result = guard(reply, goods);

        assertThat(result).isEqualTo(reply);
    }

    @Test
    @DisplayName("列举库里不存在的商品名时改为数据库摘要")
    void blocksFabricatedProduct() throws Exception {
        List<Goods> goods = List.of(goods("高等数学上册 同济第七版", "15.00", 2));
        String reply = "有高等数学和概率论、离散数学，都可以看看。";

        String result = guard(reply, goods);

        assertThat(result).startsWith("库里找到");
    }

    @Test
    @DisplayName("报价与库中不一致时改为数据库摘要")
    void blocksWrongPrice() throws Exception {
        List<Goods> goods = List.of(goods("高等数学上册 同济第七版", "15.00", 2));
        String reply = "售价300元，成色九成新。";

        String result = guard(reply, goods);

        assertThat(result).startsWith("库里找到");
    }
}
