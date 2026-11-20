package com.campus.trade.config;

import com.campus.trade.interceptor.JwtInterceptor;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.file.Path;
import java.nio.file.Paths;

@Configuration
@RequiredArgsConstructor
public class WebMvcConfig implements WebMvcConfigurer {

    private final JwtInterceptor jwtInterceptor;

    /** 图片上传的物理目录，和 FileController 用的是同一个配置项 */
    @Value("${upload.path}")
    private String uploadPath;

    /**
     * 拦截所有 /api/**，只放行登录和注册。
     * 这里靠 excludePathPatterns 精确放行，其余接口(含 AI 接口)都需要 token。
     */
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(jwtInterceptor)
                .addPathPatterns("/api/**")
                .excludePathPatterns(
                        "/api/user/login",
                        "/api/user/register"
                );
    }

    /**
     * 把上传目录映射成 /uploads/** 静态资源。
     * 不加这段的话，上传成功的图片前端拿不到，只能看到 404。
     * file: 后面必须是绝对路径且用 URI 形式（Windows 上盘符要写成 file:///D:/...），
     * 所以这里用 Path.toUri() 让 JDK 自己拼，别手写字符串。
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        Path dir = Paths.get(uploadPath).toAbsolutePath().normalize();
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations(dir.toUri().toString());
    }

    /**
     * 允许跨域的来源列表，从配置读取（cors.allowed-origins），默认只放行本机。
     * <p>
     * 之前直接放行整个 192.168/172/10 内网段 + allowCredentials(true)，
     * 意味着内网里任意站点都能带着用户凭证调本接口，太宽了。
     * 现在改为显式白名单：本机 Vite 端口不固定（5173 被占用会顺延），
     * 所以默认放行 localhost / 127.0.0.1 的任意端口；手机或另一台电脑要访问时，
     * 通过环境变量 CORS_ALLOWED_ORIGINS 显式加具体源，不再默认敞开整个内网。
     */
    @Value("${cors.allowed-origins}")
    private String[] allowedOrigins;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOriginPatterns(allowedOrigins)
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
