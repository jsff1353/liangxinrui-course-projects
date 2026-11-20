import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

public class RecallTest {
    public static void main(String[] args) throws Exception {
        Class<?> clazz = Class.forName("com.campus.trade.service.impl.AiServiceImpl");
        Constructor<?> ctor = clazz.getDeclaredConstructors()[0];
        ctor.setAccessible(true);
        Object[] ctorArgs = new Object[ctor.getParameterCount()];
        Object impl = ctor.newInstance(ctorArgs);

        Method m = clazz.getDeclaredMethod("keywordCandidates", String.class);
        m.setAccessible(true);

        String[] cases = {
                "高等数学真题",
                "高数真题",
                "英语四级真题",
                "有没有大学英语的历年真题",
                "大英真题试卷",
                "线代",
                "山地车",
                "两百块以内的耳机"
        };
        for (String s : cases) {
            Object r = m.invoke(impl, s);
            System.out.println(s + " -> " + r);
        }
    }
}
