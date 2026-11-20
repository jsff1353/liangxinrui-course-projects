package com.campus.trade.common;

import lombok.Getter;

/**
 * 业务异常：这类异常的 message 是可以直接给用户看的（"用户名已存在"）。
 * 非业务异常（SQL 报错、空指针）的 message 一律不外泄，避免暴露表结构。
 */
@Getter
public class BizException extends RuntimeException {

    private final Integer code;

    public BizException(String message) {
        this(400, message);
    }

    public BizException(Integer code, String message) {
        super(message);
        this.code = code;
    }
}
