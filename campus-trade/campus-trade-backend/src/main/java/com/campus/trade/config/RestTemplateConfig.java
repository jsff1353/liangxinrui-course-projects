package com.campus.trade.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

/**
 * 调用大模型 HTTP 接口用的 RestTemplate。
 * <p>
 * 必须显式设超时：默认的 RestTemplate 没有超时，大模型卡住时会把 Tomcat 线程一直占着，
 * 十几个并发就能把整个服务拖死（这是线上事故里非常常见的一种）。
 */
@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate aiRestTemplate(AiProperties properties) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(properties.getTimeout());
        return new RestTemplate(factory);
    }
}
