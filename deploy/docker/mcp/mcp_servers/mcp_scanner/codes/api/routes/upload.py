"""
文件上传路由模块。

仅支持压缩包上传，支持格式：.zip, .tar, .tar.gz
上传后会自动解压到任务目录。
"""

from __future__ import annotations

import io
import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

import sys
from pathlib import Path

# 添加 codes 目录到路径，以便导入 scanner 模块
# Path(__file__) = codes/api/routes/upload.py
# parent.parent.parent = codes
codes_dir = Path(__file__).parent.parent.parent
if str(codes_dir) not in sys.path:
    sys.path.insert(0, str(codes_dir))

from codes.api.models import UploadResponse
from codes.api.services.storage import StorageService
from codes.api.services.scan_service import run_scan
from scanner.output_resolver import json_output, simple_output

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

# 初始化存储服务，使用 work_dir 作为基础目录
# 注意：这里使用相对路径，实际部署时需要根据配置调整
WORK_DIR = Path(__file__).parent.parent.parent / "work_dir"
storage_service = StorageService(WORK_DIR)

# 文件大小限制：默认 500MB
MAX_FILE_SIZE = 500 * 1024 * 1024


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_files(
    file: UploadFile = File(..., description="上传的压缩包文件（支持 .zip, .tar, .tar.gz 格式）"),
    json_format: bool = Query(False, description="是否返回JSON格式的扫描结果"),
) -> UploadResponse:
    """
    上传压缩包接口。

    仅支持压缩包上传，支持格式：
    - .zip
    - .tar
    - .tar.gz

    上传后会自动解压到任务目录。

    Args:
        file: 上传的压缩包文件

    Returns:
        UploadResponse: 包含任务ID和存储路径的响应

    Raises:
        HTTPException: 文件上传失败或格式不支持
    """
    logger.info(f"收到文件上传请求: filename={file.filename}, size={file.size}, content_type={file.content_type}")
    
    # 检查文件是否存在
    if not file.filename:
        logger.warning("文件上传失败: 未提供文件名")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未提供文件名",
        )

    # 检查文件格式是否为支持的压缩包格式
    if not storage_service.is_archive_file(file.filename):
        logger.warning(f"文件上传失败: 不支持的文件格式 - {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件格式。仅支持压缩包格式: .zip, .tar, .tar.gz",
        )

    # 检查文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        logger.warning(f"文件上传失败: 文件大小超过限制 - {file.filename}, size={file.size}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制 ({MAX_FILE_SIZE / 1024 / 1024}MB)",
        )

    try:
        # 处理压缩包上传和存储
        logger.info(f"开始处理文件上传: {file.filename}")
        task_id, storage_path = await storage_service.handle_archive_upload(file)
        logger.info(f"文件上传成功: task_id={task_id}, storage_path={storage_path}")

        # 执行扫描流程
        findings = None
        try:
            logger.info(f"开始执行扫描: task_id={task_id}")
            findings = await run_scan(storage_path)
            logger.info(f"扫描完成: task_id={task_id}")
        except Exception as scan_error:
            # 扫描失败不影响上传成功，但记录错误
            logger.error(f"扫描失败: task_id={task_id}, error={str(scan_error)}", exc_info=True)
            # 可以根据需求决定是否返回错误或继续返回上传成功的响应
            pass
        
        # 根据请求参数决定返回格式
        output_content = None
        if findings:
            if json_format:
                # 返回JSON格式
                output_content = json_output(findings)
            else:
                # 返回simple格式
                output_buffer = io.StringIO()
                simple_output(findings, output=output_buffer)
                output_content = output_buffer.getvalue()
        
        logger.info(f"文件上传请求处理完成: task_id={task_id}")
        return UploadResponse(
            task_id=task_id,
            storage_path=str(storage_path),
            message="文件上传成功",
            output=output_content,
        )
    except ValueError as e:
        logger.error(f"文件上传失败 (ValueError): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"文件上传失败 (Exception): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}",
        ) from e

