"""
Pipeline 步骤路由模块。

提供独立的 pipeline 步骤 API 端点，每个步骤都可以单独调用。
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, status

from codes.api.models import (
    ResolveContextRequest,
    ResolveContextResponse,
    ScanRequest,
    PipelineScanResponse,
    DeduplicateRequest,
    DeduplicateResponse,
    serialize_scan_context,
    deserialize_scan_context,
    serialize_security_finding,
    deserialize_security_finding,
)
from codes.api.services.pipeline_service import (
    resolve_context,
    pm_scan,
    llm_scan,
    deduplicate_findings,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post(
    "/resolve-context",
    response_model=ResolveContextResponse,
    status_code=status.HTTP_200_OK,
)
async def resolve_context_endpoint(
    request: ResolveContextRequest,
) -> ResolveContextResponse:
    """
    解析目标路径，生成 ScanContext。

    Args:
        request: 解析上下文请求

    Returns:
        ResolveContextResponse: 包含序列化后的 ScanContext

    Raises:
        HTTPException: 解析失败或参数错误
    """
    try:
        logger.info(f"收到解析上下文请求: path={request.path}")
        context = await resolve_context(
            request.path,
            explicit_languages=request.explicit_languages,
            auto_detect_languages=request.auto_detect_languages,
            language_detection_limit=request.language_detection_limit,
            scan_methods=request.scan_methods,
            metadata=request.metadata,
            extension_language_map=request.extension_language_map,
        )
        context_dict = serialize_scan_context(context)
        logger.info(f"解析上下文成功: path={request.path}")
        return ResolveContextResponse(context=context_dict)
    except ValueError as e:
        logger.error(f"解析上下文失败 (ValueError): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"解析上下文失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解析上下文失败: {str(e)}",
        ) from e


@router.post(
    "/pm-scan",
    response_model=PipelineScanResponse,
    status_code=status.HTTP_200_OK,
)
async def pm_scan_endpoint(request: ScanRequest) -> PipelineScanResponse:
    """
    执行 PM Scanner 扫描。

    Args:
        request: 扫描请求，包含序列化后的 ScanContext

    Returns:
        PipelineScanResponse: 包含序列化后的 SecurityFinding 列表

    Raises:
        HTTPException: 扫描失败或参数错误
    """
    try:
        logger.info("收到 PM Scanner 扫描请求")
        # 反序列化 ScanContext
        context = deserialize_scan_context(request.context)
        # 执行扫描
        findings = await pm_scan(context)
        # 序列化结果
        findings_dict = [serialize_security_finding(f) for f in findings]
        logger.info(f"PM Scanner 扫描完成: 发现 {len(findings_dict)} 个问题")
        return PipelineScanResponse(findings=findings_dict)
    except ValueError as e:
        logger.error(f"PM Scanner 扫描失败 (ValueError): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"PM Scanner 扫描失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PM Scanner 扫描失败: {str(e)}",
        ) from e


@router.post(
    "/llm-scan",
    response_model=PipelineScanResponse,
    status_code=status.HTTP_200_OK,
)
async def llm_scan_endpoint(request: ScanRequest) -> PipelineScanResponse:
    """
    执行 LLM Scanner 扫描。

    Args:
        request: 扫描请求，包含序列化后的 ScanContext

    Returns:
        PipelineScanResponse: 包含序列化后的 SecurityFinding 列表

    Raises:
        HTTPException: 扫描失败或参数错误
    """
    try:
        logger.info("收到 LLM Scanner 扫描请求")
        # 反序列化 ScanContext
        context = deserialize_scan_context(request.context)
        # 执行扫描
        findings = await llm_scan(context)
        # 序列化结果
        findings_dict = [serialize_security_finding(f) for f in findings]
        logger.info(f"LLM Scanner 扫描完成: 发现 {len(findings_dict)} 个问题")
        return PipelineScanResponse(findings=findings_dict)
    except ValueError as e:
        logger.error(f"LLM Scanner 扫描失败 (ValueError): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"LLM Scanner 扫描失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM Scanner 扫描失败: {str(e)}",
        ) from e


@router.post(
    "/deduplicate",
    response_model=DeduplicateResponse,
    status_code=status.HTTP_200_OK,
)
async def deduplicate_endpoint(
    request: DeduplicateRequest,
) -> DeduplicateResponse:
    """
    对发现结果进行去重。

    Args:
        request: 去重请求，包含序列化后的 SecurityFinding 列表

    Returns:
        DeduplicateResponse: 包含去重后的 SecurityFinding 列表

    Raises:
        HTTPException: 去重失败或参数错误
    """
    try:
        logger.info(f"收到去重请求: {len(request.findings)} 个发现")
        # 反序列化 SecurityFinding 列表
        findings = [
            deserialize_security_finding(f) for f in request.findings
        ]
        # 执行去重
        deduplicated = await deduplicate_findings(findings)
        # 序列化结果
        findings_dict = [serialize_security_finding(f) for f in deduplicated]
        logger.info(f"去重完成: {len(findings)} -> {len(findings_dict)} 个发现")
        return DeduplicateResponse(findings=findings_dict)
    except ValueError as e:
        logger.error(f"去重失败 (ValueError): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"去重失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"去重失败: {str(e)}",
        ) from e

