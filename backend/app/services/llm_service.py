"""作用：封装 LLM 问答生成逻辑；没有 API Key 时使用本地知识库兜底回答。"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from app.core.config import settings
from app.schemas import AskRequest, Source


def _build_system_prompt(platform: str) -> str:
    """根据终端类型控制回答风格，移动端更短，PC 端可稍完整。"""
    length_rule = "回答控制在 4 句话内" if platform == "mobile" else "回答使用 3 到 5 个要点"
    return (
        "你是三资管理智能助手，服务对象是村级经办人员。"
        "请用通俗、明确、可操作的语言回答，不要大段照搬政策原文。"
        f"{length_rule}，必须说明办理步骤、注意事项和可追问方向。"
    )


def _build_user_prompt(question: str, sources: list[Source]) -> str:
    """把用户问题和检索到的资料拼成模型输入。"""
    source_text = "\n".join(
        f"[{source.id}] {source.title}（{source.category}）：{source.excerpt}"
        for source in sources
    )
    return f"用户问题：{question}\n\n可参考资料：\n{source_text}"


def _local_answer(payload: AskRequest, sources: list[Source]) -> tuple[str, list[str], str]:
    """无真实模型时生成结构化兜底回答，保证项目演示完整可跑。"""
    first_source = sources[0] if sources else None
    source_hint = f"参考《{first_source.title}》" if first_source else "建议先补充本地业务材料"
    mobile = payload.platform == "mobile"

    if mobile:
        answer = (
            f"{source_hint}，这个问题可以先按“确认事项、查资料、走流程、留痕公示”四步处理。"
            "先明确涉及资金、资产还是资源，再核对审批权限和材料清单。"
            "办理时注意保留会议记录、审批单、合同或票据，避免口头处理。"
            "如果你提供具体场景，我可以继续帮你拆成操作步骤。"
        )
    else:
        answer = (
            f"{source_hint}，建议按下面方式处理：\n"
            "1. 先判断问题属于资金收支、资产处置还是资源发包，确定适用制度。\n"
            "2. 对照材料清单准备会议记录、审批表、合同、票据和公示材料。\n"
            "3. 按村级申请、民主议事、乡镇审核、平台录入、公示归档的顺序推进。\n"
            "4. 重点检查金额、期限、承包主体、审批权限和公开公示是否完整。\n"
            "5. 如遇到特殊事项，应补充上级政策依据或请主管部门确认。"
        )

    suggestions = [
        "这个事项需要准备哪些材料？",
        "资金支出审批流程怎么走？",
        "资源发包需要注意哪些风险？",
    ]
    return answer, suggestions, "local_fallback"


async def answer_question(
    payload: AskRequest,
    sources: list[Source],
) -> tuple[str, list[str], str]:
    """优先调用真实 LLM，失败或无 Key 时降级到本地回答。"""
    if not settings.openai_api_key:
        return _local_answer(payload, sources)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": _build_system_prompt(payload.platform.value)},
                {"role": "user", "content": _build_user_prompt(payload.question, sources)},
            ],
            temperature=0.2,
        )
        answer = response.choices[0].message.content or ""
        suggestions = [
            "能否给我一个办理清单？",
            "这个流程有哪些常见错误？",
            "移动端录入时要注意什么？",
        ]
        return answer.strip(), suggestions, "llm"
    except Exception:
        return _local_answer(payload, sources)


_STREAM_CHUNK_SIZE = 24
_STREAM_INTERVAL_SECONDS = 0.04


async def _stream_local(
    payload: AskRequest,
    sources: list[Source],
) -> AsyncIterator[tuple[str, object]]:
    """把本地兜底回答按字符分片成流，模拟 LLM token 输出。"""
    answer, suggestions, mode = _local_answer(payload, sources)
    for index in range(0, len(answer), _STREAM_CHUNK_SIZE):
        yield "delta", answer[index : index + _STREAM_CHUNK_SIZE]
        await asyncio.sleep(_STREAM_INTERVAL_SECONDS)
    yield "suggestions", suggestions
    yield "mode", mode


async def _stream_llm(
    payload: AskRequest,
    sources: list[Source],
) -> AsyncIterator[tuple[str, object]]:
    """调用 OpenAI 流式接口，逐 token 产出 delta。"""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    stream = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": _build_system_prompt(payload.platform.value)},
            {"role": "user", "content": _build_user_prompt(payload.question, sources)},
        ],
        temperature=0.2,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield "delta", delta
    yield "suggestions", [
        "能否给我一个办理清单？",
        "这个流程有哪些常见错误？",
        "移动端录入时要注意什么？",
    ]
    yield "mode", "llm"


async def stream_answer(
    payload: AskRequest,
    sources: list[Source],
) -> AsyncIterator[tuple[str, object]]:
    """统一的流式入口：无 Key 或失败时回退到本地分片流。"""
    if not settings.openai_api_key:
        async for event in _stream_local(payload, sources):
            yield event
        return

    try:
        async for event in _stream_llm(payload, sources):
            yield event
    except Exception:
        async for event in _stream_local(payload, sources):
            yield event

