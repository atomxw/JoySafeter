"""
MCP 服务器模块。

提供代码扫描服务的 MCP 接口，将现有服务功能暴露为 MCP 工具。
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from codes.api.models import (
    serialize_scan_context,
    serialize_security_finding,
    deserialize_scan_context,
    deserialize_security_finding,
)
from codes.api.services.pipeline_service import (
    resolve_context,
    pm_scan,
    llm_scan,
    deduplicate_findings,
)
from codes.api.services.scan_service import run_scan
from codes.api.services.storage import StorageService

logger = logging.getLogger(__name__)

# 初始化存储服务
WORK_DIR = Path(__file__).parent.parent.parent / "work_dir"
storage_service = StorageService(WORK_DIR)

# 创建 MCP 服务器
mcp = FastMCP("Code Security Scanner")


def clone_git_repository(
    url: str, target_dir: Path, ref: str | None = None, token: str | None = None
) -> None:
    """
    克隆 Git 仓库到目标目录。

    Args:
        url: Git 仓库 URL
        target_dir: 目标目录
        ref: 分支/标签/提交（可选）
        token: 访问令牌（可选，用于私有仓库）

    Raises:
        ValueError: Git 克隆失败
    """
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    # 如果有 token，将其添加到 URL 中
    auth_url = url
    if token:
        # 支持不同格式的 URL
        if url.startswith("https://"):
            # https://github.com/user/repo.git -> https://token@github.com/user/repo.git
            if "@" not in url:
                auth_url = url.replace("https://", f"https://{token}@")
        elif url.startswith("git@"):
            # SSH 格式，token 需要在配置中设置
            # 这里简化处理，如果需要 SSH 认证，可以通过环境变量配置
            pass

    try:
        # 构建 git clone 命令
        cmd = ["git", "clone", "--depth", "1", auth_url, str(target_dir)]

        # 如果指定了 ref（分支/标签），在克隆时指定分支
        if ref:
            cmd = ["git", "clone", "--depth", "1", "--branch", ref, auth_url, str(target_dir)]

        # 执行 git clone
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            # 如果失败，清理已创建的目录
            if target_dir.exists():
                import shutil
                shutil.rmtree(target_dir, ignore_errors=True)
            raise ValueError(
                f"Git 克隆失败: {result.stderr or result.stdout or '未知错误'}"
            )
    except FileNotFoundError:
        raise ValueError("未找到 git 命令，请确保已安装 Git")
    except Exception as e:
        if target_dir.exists():
            import shutil
            shutil.rmtree(target_dir, ignore_errors=True)
        raise ValueError(f"Git 克隆失败: {str(e)}") from e


@mcp.tool()
async def scan_code_from_path(
    path: str,
    explicit_languages: list[str] | None = None,
    auto_detect_languages: bool = True,
    language_detection_limit: int = 5000,
) -> dict[str, Any]:
    """
    扫描指定路径的代码，执行完整的扫描流程（包括 PM Scanner 和 LLM Scanner）。

    Args:
        path: 要扫描的代码路径（本地文件系统路径）
        explicit_languages: 显式指定的编程语言列表（可选）
        auto_detect_languages: 是否自动检测语言，默认为 True
        language_detection_limit: 语言检测的最大文件数，默认为 5000

    Returns:
        包含扫描结果的字典，包括：
        - findings: 发现的安全问题列表
        - count: 问题数量
        - path: 扫描的路径
    """
    try:
        logger.info(f"MCP: 开始扫描路径: {path}")
        
        # 执行完整扫描流程
        findings = await run_scan(path)
        
        # 序列化结果
        findings_dict = [serialize_security_finding(f) for f in findings]
        
        logger.info(f"MCP: 扫描完成，发现 {len(findings_dict)} 个问题")
        
        return {
            "findings": findings_dict,
            "count": len(findings_dict),
            "path": path,
        }
    except Exception as e:
        logger.error(f"MCP: 扫描失败: {str(e)}", exc_info=True)
        return {
            "error": f"扫描失败: {str(e)}",
            "path": path,
        }


@mcp.tool()
async def scan_code_from_git(
    url: str,
    ref: str | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    """
    从 Git 仓库克隆并扫描代码。

    Args:
        url: Git 仓库 URL（例如：https://github.com/user/repo.git）
        ref: 分支/标签/提交（可选，默认为默认分支）
        token: 访问令牌（可选，用于私有仓库）

    Returns:
        包含扫描结果的字典，包括：
        - findings: 发现的安全问题列表
        - count: 问题数量
        - task_id: 任务ID
        - storage_path: 存储路径
    """
    try:
        logger.info(f"MCP: 开始克隆 Git 仓库: {url}")
        
        # 生成任务ID和目录
        task_id = storage_service.generate_task_id()
        task_dir = storage_service.create_task_directory(task_id)
        
        # 克隆 Git 仓库
        clone_git_repository(
            url=url.strip(),
            target_dir=task_dir,
            ref=ref,
            token=token,
        )
        
        logger.info(f"MCP: Git 仓库克隆成功: {task_id}")
        
        # 执行扫描流程
        findings = None
        try:
            findings = await run_scan(task_dir)
        except Exception as scan_error:
            logger.error(f"MCP: 扫描失败: {str(scan_error)}", exc_info=True)
            return {
                "error": f"扫描失败: {str(scan_error)}",
                "task_id": task_id,
                "storage_path": str(task_dir),
            }
        
        # 序列化结果
        findings_dict = [serialize_security_finding(f) for f in findings] if findings else []
        
        logger.info(f"MCP: 扫描完成，发现 {len(findings_dict)} 个问题")
        
        return {
            "findings": findings_dict,
            "count": len(findings_dict),
            "task_id": task_id,
            "storage_path": str(task_dir),
        }
    except Exception as e:
        logger.error(f"MCP: Git 扫描失败: {str(e)}", exc_info=True)
        return {
            "error": f"Git 扫描失败: {str(e)}",
            "url": url,
        }


@mcp.tool()
async def resolve_scan_context(
    path: str,
    explicit_languages: list[str] | None = None,
    auto_detect_languages: bool = True,
    language_detection_limit: int = 5000,
    scan_methods: dict[str, Any] | list[str] | None = None,
    metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    解析目标路径，生成扫描上下文（ScanContext）。

    Args:
        path: 目标路径（字符串）
        explicit_languages: 显式指定的语言列表（可选）
        auto_detect_languages: 是否自动检测语言，默认为 True
        language_detection_limit: 语言检测的最大文件数，默认为 5000
        scan_methods: 扫描方法配置（可选）
        metadata: 用户元数据（可选）

    Returns:
        包含序列化后的 ScanContext 的字典
    """
    try:
        logger.info(f"MCP: 解析扫描上下文: {path}")
        
        context = await resolve_context(
            path,
            explicit_languages=explicit_languages,
            auto_detect_languages=auto_detect_languages,
            language_detection_limit=language_detection_limit,
            scan_methods=scan_methods,
            metadata=metadata,
        )
        
        context_dict = serialize_scan_context(context)
        logger.info(f"MCP: 解析上下文成功: {path}")
        
        return {"context": context_dict}
    except Exception as e:
        logger.error(f"MCP: 解析上下文失败: {str(e)}", exc_info=True)
        return {
            "error": f"解析上下文失败: {str(e)}",
            "path": path,
        }


@mcp.tool()
async def run_pm_scan(
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    执行 PM Scanner 扫描（基于规则的静态分析）。

    Args:
        context: 序列化后的 ScanContext 字典（可通过 resolve_scan_context 获取）

    Returns:
        包含扫描结果的字典，包括：
        - findings: 发现的安全问题列表
        - count: 问题数量
    """
    try:
        logger.info("MCP: 执行 PM Scanner 扫描")
        
        # 反序列化 ScanContext
        scan_context = deserialize_scan_context(context)
        
        # 执行扫描
        findings = await pm_scan(scan_context)
        
        # 序列化结果
        findings_dict = [serialize_security_finding(f) for f in findings]
        
        logger.info(f"MCP: PM Scanner 扫描完成: 发现 {len(findings_dict)} 个问题")
        
        return {
            "findings": findings_dict,
            "count": len(findings_dict),
        }
    except Exception as e:
        logger.error(f"MCP: PM Scanner 扫描失败: {str(e)}", exc_info=True)
        return {
            "error": f"PM Scanner 扫描失败: {str(e)}",
        }


@mcp.tool()
async def run_llm_scan(
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    执行 LLM Scanner 扫描（基于大语言模型的代码分析）。

    Args:
        context: 序列化后的 ScanContext 字典（可通过 resolve_scan_context 获取）

    Returns:
        包含扫描结果的字典，包括：
        - findings: 发现的安全问题列表
        - count: 问题数量
    """
    try:
        logger.info("MCP: 执行 LLM Scanner 扫描")
        
        # 反序列化 ScanContext
        scan_context = deserialize_scan_context(context)
        
        # 执行扫描
        findings = await llm_scan(scan_context)
        
        # 序列化结果
        findings_dict = [serialize_security_finding(f) for f in findings]
        
        logger.info(f"MCP: LLM Scanner 扫描完成: 发现 {len(findings_dict)} 个问题")
        
        return {
            "findings": findings_dict,
            "count": len(findings_dict),
        }
    except Exception as e:
        logger.error(f"MCP: LLM Scanner 扫描失败: {str(e)}", exc_info=True)
        return {
            "error": f"LLM Scanner 扫描失败: {str(e)}",
        }


@mcp.tool()
async def deduplicate_findings(
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    对扫描结果进行去重，移除重复的安全问题。

    Args:
        findings: 序列化后的 SecurityFinding 列表

    Returns:
        包含去重后结果的字典，包括：
        - findings: 去重后的安全问题列表
        - count: 去重后的问题数量
        - original_count: 原始问题数量
    """
    try:
        logger.info(f"MCP: 开始去重: {len(findings)} 个发现")
        
        # 反序列化 SecurityFinding 列表
        findings_objects = [
            deserialize_security_finding(f) for f in findings
        ]
        
        # 执行去重
        deduplicated = await deduplicate_findings(findings_objects)
        
        # 序列化结果
        findings_dict = [serialize_security_finding(f) for f in deduplicated]
        
        logger.info(f"MCP: 去重完成: {len(findings)} -> {len(findings_dict)} 个发现")
        
        return {
            "findings": findings_dict,
            "count": len(findings_dict),
            "original_count": len(findings),
        }
    except Exception as e:
        logger.error(f"MCP: 去重失败: {str(e)}", exc_info=True)
        return {
            "error": f"去重失败: {str(e)}",
            "original_count": len(findings),
        }

