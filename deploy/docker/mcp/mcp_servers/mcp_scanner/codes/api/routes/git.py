"""
Git 链接路由模块。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from codes.api.models import GitScanRequest, GitScanResponse, serialize_report
from codes.api.services.storage import StorageService
from codes.api.services.scan_service import run_scan

router = APIRouter(prefix="/api", tags=["git"])

# 初始化存储服务
WORK_DIR = Path(__file__).parent.parent.parent / "work_dir"
storage_service = StorageService(WORK_DIR)


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

        # 如果指定了 ref（分支/标签），在克隆后 checkout
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


@router.post("/scan/git", response_model=GitScanResponse, status_code=status.HTTP_201_CREATED)
async def scan_git_repository(request: GitScanRequest) -> GitScanResponse:
    """
    通过 Git 链接扫描代码仓库。

    Args:
        request: Git 扫描请求，包含 URL、分支/标签（可选）、访问令牌（可选）

    Returns:
        GitScanResponse: 包含任务ID和存储路径的响应

    Raises:
        HTTPException: Git 克隆失败或参数错误
    """
    if not request.url or not request.url.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Git 仓库 URL 不能为空",
        )

    try:
        # 生成任务ID和目录
        task_id = storage_service.generate_task_id()
        task_dir = storage_service.create_task_directory(task_id)

        # 克隆 Git 仓库
        clone_git_repository(
            url=request.url.strip(),
            target_dir=task_dir,
            ref=request.ref,
            token=request.token,
        )

        # 执行扫描流程
        findings = None
        try:
            findings = await run_scan(task_dir)
        except Exception as scan_error:
            # 扫描失败不影响克隆成功，但记录错误
            # 可以根据需求决定是否返回错误或继续返回克隆成功的响应
            pass

        # 序列化报告
        report_dict = None
        if findings:
            report_dict = serialize_report(findings)

        return GitScanResponse(
            task_id=task_id,
            storage_path=str(task_dir),
            message="Git 仓库克隆成功",
            report=report_dict,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理 Git 仓库失败: {str(e)}",
        ) from e

