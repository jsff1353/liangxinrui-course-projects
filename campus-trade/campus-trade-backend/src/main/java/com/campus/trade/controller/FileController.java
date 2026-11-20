package com.campus.trade.controller;

import com.campus.trade.common.BizException;
import com.campus.trade.common.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * 图片上传。
 * <p>
 * 三个必须自己做的防护（Spring 默认一个都不给）：
 * 1. 校验大小，防止有人传个 2G 的包把磁盘塞满；
 * 2. 校验后缀白名单，防止传 .jsp/.exe 之类的可执行文件；
 * 3. 文件名用 UUID 重新生成，绝不使用用户传的原始文件名——
 *    否则形如 "../../application.yml" 的名字会把文件写到目录外面去（路径穿越）。
 */
@Slf4j
@RestController
@RequestMapping("/api/file")
public class FileController {

    /** 允许的图片后缀 */
    private static final List<String> ALLOWED_EXT = List.of("jpg", "jpeg", "png", "webp", "gif");

    /** 单张图片上限 5MB，和 application.yml 里的 multipart 限制保持一致 */
    private static final long MAX_SIZE = 5 * 1024 * 1024L;

    @Value("${upload.path}")
    private String uploadPath;

    /** 上传图片：POST /api/file/upload，表单字段名必须是 file */
    @PostMapping("/upload")
    public Result<String> upload(@RequestParam("file") MultipartFile file) throws IOException {
        if (file == null || file.isEmpty()) {
            throw new BizException("请选择要上传的图片");
        }
        if (file.getSize() > MAX_SIZE) {
            throw new BizException("图片不能超过 5MB");
        }

        String ext = getExt(file.getOriginalFilename());
        if (!ALLOWED_EXT.contains(ext)) {
            throw new BizException("只支持 jpg / png / webp / gif 格式的图片");
        }
        // 光看后缀不够：把木马改名成 .jpg 就能绕过白名单。再验一遍文件头 magic number，
        // 确认内容确实是声明的图片类型（上传目录被静态映射，虽不执行 JSP，仍要挡住伪装文件）。
        if (!hasImageHeader(file, ext)) {
            throw new BizException("图片内容与格式不符，请上传真实图片");
        }

        // 按日期分目录，避免所有图片堆在一个文件夹里（以后迁移到 OSS 也好对应）
        String day = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String fileName = UUID.randomUUID().toString().replace("-", "") + "." + ext;

        Path dir = Paths.get(uploadPath, day).toAbsolutePath().normalize();
        Files.createDirectories(dir);

        Path target = dir.resolve(fileName).normalize();
        // 双保险：确认最终落盘路径确实在上传目录之内
        if (!target.startsWith(dir)) {
            throw new BizException("非法的文件名");
        }
        file.transferTo(target.toFile());
        log.info("图片上传成功: {}", target);

        // 返回相对路径，前端拼 /uploads 前缀访问
        return Result.ok("/uploads/" + day + "/" + fileName);
    }

    /**
     * 读取文件头前若干字节，比对图片格式的 magic number。
     * <pre>
     *   jpg/jpeg : FF D8 FF
     *   png      : 89 50 4E 47 0D 0A 1A 0A
     *   gif      : GIF87a / GIF89a
     *   webp     : RIFF....WEBP（第 0~3 字节 RIFF，第 8~11 字节 WEBP）
     * </pre>
     * 读完后流会自动回到开头（MultipartFile 每次 getInputStream 都是新流），不影响后续 transferTo。
     */
    private boolean hasImageHeader(MultipartFile file, String ext) {
        byte[] head = new byte[12];
        int read;
        try (InputStream in = file.getInputStream()) {
            read = in.read(head);
        } catch (IOException e) {
            log.warn("读取图片头失败: {}", e.toString());
            return false;
        }
        if (read < 3) {
            return false;
        }
        int b0 = head[0] & 0xFF, b1 = head[1] & 0xFF, b2 = head[2] & 0xFF;
        switch (ext) {
            case "jpg":
            case "jpeg":
                return b0 == 0xFF && b1 == 0xD8 && b2 == 0xFF;
            case "png":
                return read >= 8 && b0 == 0x89 && b1 == 0x50 && b2 == 0x4E && head[3] == 0x47
                        && head[4] == 0x0D && head[5] == 0x0A && head[6] == 0x1A && head[7] == 0x0A;
            case "gif":
                return read >= 6 && head[0] == 'G' && head[1] == 'I' && head[2] == 'F' && head[3] == '8';
            case "webp":
                return read >= 12 && head[0] == 'R' && head[1] == 'I' && head[2] == 'F' && head[3] == 'F'
                        && head[8] == 'W' && head[9] == 'E' && head[10] == 'B' && head[11] == 'P';
            default:
                return false;
        }
    }

    private String getExt(String originalName) {
        if (originalName == null) {
            return "";
        }
        int dot = originalName.lastIndexOf('.');
        if (dot < 0 || dot == originalName.length() - 1) {
            return "";
        }
        return originalName.substring(dot + 1).toLowerCase(Locale.ROOT);
    }
}
