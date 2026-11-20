package com.campus.trade.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

/**
 * 大模型配置，对应 application.yml 里的 ai.* 节点。
 * <p>
 * 默认对接智谱 GLM-4-Flash：免费额度够毕设演示用，接口协议和 OpenAI 完全兼容，
 * 换成 DeepSeek / 通义 只需要改 base-url 和 model 两个值。
 */
@Data
@Component
@ConfigurationProperties(prefix = "ai")
public class AiProperties {

    /** API Key。留空则整个 AI 模块自动降级为本地检索，不会报错，也不影响其他功能 */
    private String apiKey;

    /** 接口根地址 */
    private String baseUrl = "https://open.bigmodel.cn/api/paas/v4";

    /** 模型名 */
    private String model = "glm-4-flash";

    /** 超时（毫秒）。大模型首字延迟经常 2~5 秒，给太短会频繁失败 */
    private int timeout = 20000;

    public boolean isEnabled() {
        return StringUtils.hasText(apiKey);
    }
}
