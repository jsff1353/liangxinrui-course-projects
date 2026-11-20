package com.campus.trade.controller;

import com.campus.trade.common.Result;
import com.campus.trade.dto.AiChatDTO;
import com.campus.trade.service.AiService;
import com.campus.trade.vo.AiChatVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * AI 智能模块。
 * <p>
 * 已对接真实大模型（智谱 GLM-4-Flash，OpenAI 协议兼容）：
 * 智能导购是支持多轮对话的智能体，走 Function Calling —— 模型只会提出查询条件，
 * 真实商品由后端查库回填，从结构上杜绝编造商品；
 * 没配 Key 或调用失败时自动降级为本地检索/模板文案，接口不会 500。
 */
@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
public class AiController {

    private final AiService aiService;

    /**
     * 智能导购对话：POST /api/ai/chat
     * <p>
     * 请求体里带完整的多轮消息，前端只负责把历史消息原样发上来，会话状态由模型自己维护。
     */
    @PostMapping("/chat")
    public Result<AiChatVO> chat(@RequestBody @Valid AiChatDTO dto) {
        return Result.ok(aiService.chat(dto.getMessages()));
    }

    /**
     * 智能发布助手：POST /api/ai/generate-desc?title=二手自行车&category=运动&itemCondition=2
     */
    @PostMapping("/generate-desc")
    public Result<String> generateDescByAi(@RequestParam String title,
                                           @RequestParam(required = false) String category,
                                           @RequestParam(required = false) Integer itemCondition) {
        if (title == null || title.isBlank()) {
            return Result.fail("请先填写商品标题");
        }
        return Result.ok(aiService.generateDescription(title.trim(), category, itemCondition));
    }
}
