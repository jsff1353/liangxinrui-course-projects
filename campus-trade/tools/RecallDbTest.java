import com.baomidou.mybatisplus.core.MybatisConfiguration;
import com.baomidou.mybatisplus.core.MybatisSqlSessionFactoryBuilder;
import com.campus.trade.entity.Goods;
import com.campus.trade.mapper.GoodsMapper;
import org.apache.ibatis.datasource.unpooled.UnpooledDataSource;
import org.apache.ibatis.mapping.Environment;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.apache.ibatis.transaction.jdbc.JdbcTransactionFactory;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.util.List;

/**
 * 用真实 MySQL 跑一遍 AiServiceImpl.queryGoods 的多级召回，
 * 验证拼接出来的 SQL 正确、且"高等数学真题""英语四级真题""山地车"都能查到。
 */
public class RecallDbTest {

    public static void main(String[] args) throws Exception {
        UnpooledDataSource ds = new UnpooledDataSource(
                "com.mysql.cj.jdbc.Driver",
                "jdbc:mysql://localhost:3306/campus_trade?useUnicode=true&characterEncoding=utf8"
                        + "&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true&useSSL=false",
                "root", "123456");
        MybatisConfiguration cfg = new MybatisConfiguration();
        cfg.setEnvironment(new Environment("test", new JdbcTransactionFactory(), ds));
        cfg.setMapUnderscoreToCamelCase(true);
        cfg.addMapper(GoodsMapper.class);
        SqlSessionFactory factory = new MybatisSqlSessionFactoryBuilder().build(cfg);

        try (SqlSession session = factory.openSession()) {
            GoodsMapper mapper = session.getMapper(GoodsMapper.class);

            Class<?> clazz = Class.forName("com.campus.trade.service.impl.AiServiceImpl");
            Constructor<?> ctor = clazz.getDeclaredConstructors()[0];
            ctor.setAccessible(true);
            Object[] ctorArgs = new Object[ctor.getParameterCount()];
            ctorArgs[ctor.getParameterCount() - 1] = mapper;
            Object impl = ctor.newInstance(ctorArgs);

            Method m = clazz.getDeclaredMethod("queryGoods", String.class, String.class,
                    BigDecimal.class, BigDecimal.class);
            m.setAccessible(true);

            probe(m, impl, "用户问法：有高等数学的真题吗", "高等数学真题", "教材");
            probe(m, impl, "用户问法：英语四级真题有吗", "英语四级真题", "教材");
            probe(m, impl, "用户问法：高数真题", "高数真题", null);
            probe(m, impl, "用户问法：有山地车吗", "山地车", null);
            probe(m, impl, "用户问法：两百块以内的键盘", "键盘", "数码");
            probe(m, impl, "用户问法：有没有教材", null, "教材");
            probe(m, impl, "用户问法：有没有书", "书", null);
            probe(m, impl, "用户问法：有没有教材（关键词）", "教材", null);
            probe(m, impl, "用户问法：有没有线性代数", "线性代数", null);
            probe(m, impl, "用户问法：有没有显卡", "显卡", null);
            probe(m, impl, "用户问法：有没有WiFi", "WiFi", null);
            probe(m, impl, "用户问法：有没有第九代", "第九代", null);
            probe(m, impl, "用户问法：有没有第9代", "第9代", null);
            probe(m, impl, "用户问法：有没有第 9 代", "第 9 代", null);
            probe(m, impl, "用户问法：有没有64G", "64G", null);
            probe(m, impl, "用户问法：有没有版", "版", null);
            probe(m, impl, "用户问法：有没有平板（整句）", "有没有平板", null);
            probe(m, impl, "用户问法：有没有平板电脑", "平板电脑", null);
            probe(m, impl, "用户问法：有没有相机（整句）", "有没有相机", null);

            Method gq = clazz.getDeclaredMethod("looksLikeGoodsQuery", String.class);
            gq.setAccessible(true);
            System.out.println("intent-有没有平板: " + gq.invoke(impl, "有没有平板"));
            System.out.println("intent-怎么付款: " + gq.invoke(impl, "怎么付款"));
            System.out.println("intent-你好: " + gq.invoke(impl, "你好"));

            Method fr = clazz.getDeclaredMethod("finalReply", String.class, List.class, boolean.class);
            fr.setAccessible(true);
            List<Goods> hit = query(m, impl, "高等数学真题", "教材");
            System.out.println("guard-书名幻觉(有商品): "
                    + fr.invoke(impl, "当然有，比如《高等数学》、《线性代数》、《概率论》等", hit, true));
            System.out.println("guard-零召回: "
                    + fr.invoke(impl, "当然有，书这里也有很多，比如《高等数学》、《线性代数》、《概率论》等", List.of(), true));
            System.out.println("guard-纯咨询不调工具: "
                    + fr.invoke(impl, "下单后请在 2 小时内付款，超时会自动取消。", List.of(), false));
            System.out.println("guard-价格错: "
                    + fr.invoke(impl, "这本山地车 300 元，八成新。", query(m, impl, "山地车", null), true));
            System.out.println("guard-列举幻觉(有商品，无书名号): "
                    + fr.invoke(impl, "当然有，我查到了一些教材，比如高等数学、线性代数、概率论等，你要找哪一本呢？",
                            query(m, impl, "书", null), true));
            System.out.println("guard-正常单品回答: "
                    + fr.invoke(impl, "有的，高等数学 第七版 上下册 25 元，九成新。",
                            query(m, impl, "高等数学真题", "教材"), true));
            System.out.println("guard-未调工具却假装搜索: "
                    + fr.invoke(impl, "好的，我帮你找找。稍等一下…（经过搜索，我找到了一本线性代数教材，全新，价格是30元。）",
                            List.of(), false));
        }
    }

    private static List<Goods> query(Method m, Object impl, String keyword, String category)
            throws Exception {
        @SuppressWarnings("unchecked")
        List<Goods> list = (List<Goods>) m.invoke(impl, keyword, category, null, null);
        return list;
    }

    private static void probe(Method m, Object impl, String label, String keyword, String category)
            throws Exception {
        @SuppressWarnings("unchecked")
        List<Goods> list = (List<Goods>) m.invoke(impl, keyword, category, null, null);
        StringBuilder sb = new StringBuilder();
        sb.append(label).append("  [kw=").append(keyword).append(", cat=").append(category).append("] -> ");
        if (list.isEmpty()) {
            sb.append("空");
        } else {
            sb.append(list.size()).append(" 件：");
            for (Goods g : list) {
                sb.append(g.getId()).append("-").append(g.getTitle()).append("￥").append(g.getPrice()).append("  ");
            }
        }
        System.out.println(sb);
    }
}
