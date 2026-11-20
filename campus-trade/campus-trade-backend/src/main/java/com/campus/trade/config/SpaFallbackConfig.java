package com.campus.trade.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.Resource;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.resource.PathResourceResolver;

import java.io.IOException;

/**
 * 单页应用（SPA）路由回退。
 * <p>
 * 前端用的是 history 模式（createWebHistory），刷新 /goods/5 时浏览器会真的向后端请求
 * GET /goods/5，后端没有这个接口，于是 404 —— 这是打包成一个 jar 之后最典型的坑。
 * <p>
 * 解决思路：静态资源找不到文件时，只要不是 /api 和 /uploads 开头的请求，
 * 就返回 index.html，剩下的路由交给 Vue Router 自己解析。
 * 用资源解析器实现而不是 `@GetMapping("/**")`，是因为后者会把 /uploads 里的图片也吃掉。
 */
@Configuration
public class SpaFallbackConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/**")
                .addResourceLocations("classpath:/static/")
                .resourceChain(true)
                .addResolver(new PathResourceResolver() {
                    @Override
                    protected Resource getResource(String resourcePath, Resource location) throws IOException {
                        // 后端接口和上传的图片不参与回退
                        if (resourcePath.startsWith("api/") || resourcePath.startsWith("uploads/")) {
                            return null;
                        }
                        if (!resourcePath.isEmpty()) {
                            Resource requested = location.createRelative(resourcePath);
                            if (requested.exists() && requested.isReadable()) {
                                return requested;
                            }
                        }
                        // 找不到就回退到首页，由前端路由接管
                        Resource index = location.createRelative("index.html");
                        return index.exists() ? index : null;
                    }
                });
    }
}
