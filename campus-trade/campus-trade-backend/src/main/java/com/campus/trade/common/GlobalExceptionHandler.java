package com.campus.trade.common;

import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 全局异常兜底，保证前端永远拿到 Result 结构的 JSON。
 *
 * 分三类处理，关键是"哪些 message 能给前端看"：
 *   1. BizException          -> 业务提示，原样返回（"商品已售出，无法下单"）
 *   2. 参数校验异常            -> 返回第一条校验失败的提示
 *   3. 其他 Exception         -> 只返回"系统繁忙"，真实堆栈写日志
 * 第 3 条很重要：直接吐 e.getMessage() 会把 SQL 表名、字段名暴露给用户。
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizException.class)
    public Result<Void> handleBiz(BizException e) {
        return Result.fail(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValid(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
                .map(f -> f.getDefaultMessage())
                .findFirst()
                .orElse("参数校验失败");
        return Result.fail(400, msg);
    }

    /** 唯一索引冲突：并发注册同一个用户名时数据库抛的，转成友好提示 */
    @ExceptionHandler(DuplicateKeyException.class)
    public Result<Void> handleDuplicate(DuplicateKeyException e) {
        log.warn("唯一索引冲突: {}", e.getMessage());
        return Result.fail(400, "数据已存在，请勿重复提交");
    }

    @ExceptionHandler(Exception.class)
    public Result<Void> handleOther(Exception e) {
        // 堆栈进日志，前端只看到"系统繁忙"
        log.error("系统异常", e);
        return Result.fail(500, "系统繁忙，请稍后重试");
    }
}
