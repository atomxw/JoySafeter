"""
文件存储服务模块。
"""

from __future__ import annotations

import shutil
import tarfile
import uuid
import zipfile
from pathlib import Path

from fastapi import UploadFile


class StorageService:
    """文件存储服务，处理文件上传、压缩包解压和目录管理。"""

    def __init__(self, base_dir: Path) -> None:
        """
        初始化存储服务。

        Args:
            base_dir: 工作目录基础路径（例如 work_dir）
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def generate_task_id(self) -> str:
        """生成唯一任务ID。"""
        return str(uuid.uuid4())

    def create_task_directory(self, task_id: str) -> Path:
        """
        为任务创建唯一目录。

        Args:
            task_id: 任务ID

        Returns:
            创建的任务目录路径
        """
        task_dir = self.base_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir

    def save_uploaded_files(
        self, files: list[UploadFile], task_dir: Path
    ) -> None:
        """
        保存上传的文件到任务目录。

        Args:
            files: 上传的文件列表
            task_dir: 任务目录路径
        """
        for file in files:
            if file.filename:
                file_path = task_dir / file.filename
                # 如果文件已存在，创建唯一名称
                if file_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    counter = 1
                    while file_path.exists():
                        file_path = task_dir / f"{stem}_{counter}{suffix}"
                        counter += 1

                # 保存文件
                with open(file_path, "wb") as f:
                    content = file.file.read()
                    f.write(content)
                    file.file.seek(0)  # 重置文件指针，以便后续处理

    def extract_archive(self, archive_path: Path, extract_to: Path) -> None:
        """
        解压压缩包到目标目录。

        支持格式：zip, tar, tar.gz

        Args:
            archive_path: 压缩包路径
            extract_to: 解压目标目录

        Raises:
            ValueError: 不支持的压缩包格式
            Exception: 解压失败
        """
        archive_path = Path(archive_path)
        extract_to = Path(extract_to)
        extract_to.mkdir(parents=True, exist_ok=True)

        suffix = archive_path.suffix.lower()

        if suffix == ".zip":
            self._extract_zip(archive_path, extract_to)
        elif suffix == ".tar":
            self._extract_tar(archive_path, extract_to)
        elif archive_path.suffixes == [".tar", ".gz"]:
            self._extract_tar_gz(archive_path, extract_to)
        else:
            raise ValueError(
                f"不支持的压缩包格式: {suffix}. 支持格式: .zip, .tar, .tar.gz"
            )

        self._cleanup_macos_artifacts(extract_to)

    def _extract_zip(self, archive_path: Path, extract_to: Path) -> None:
        """解压 ZIP 文件。"""
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

    def _extract_tar(self, archive_path: Path, extract_to: Path) -> None:
        """解压 TAR 文件。"""
        with tarfile.open(archive_path, "r") as tar_ref:
            tar_ref.extractall(extract_to)

    def _extract_tar_gz(self, archive_path: Path, extract_to: Path) -> None:
        """解压 TAR.GZ 文件。"""
        with tarfile.open(archive_path, "r:gz") as tar_ref:
            tar_ref.extractall(extract_to)

    def _cleanup_macos_artifacts(self, target_dir: Path) -> None:
        """删除 macOS 解压产生的额外文件，如 ._* 和 __MACOSX 目录。"""
        for apple_double in target_dir.rglob("._*"):
            if apple_double.is_file():
                apple_double.unlink(missing_ok=True)

        for macos_dir in target_dir.rglob("__MACOSX"):
            if macos_dir.is_dir():
                shutil.rmtree(macos_dir, ignore_errors=True)

    def is_archive_file(self, filename: str) -> bool:
        """
        检查文件是否为支持的压缩包格式。

        Args:
            filename: 文件名

        Returns:
            是否为压缩包
        """
        if not filename:
            return False
        path = Path(filename)
        suffixes = [s.lower() for s in path.suffixes]
        return (
            ".zip" in suffixes
            or ".tar" in suffixes
            or (".tar" in suffixes and ".gz" in suffixes)
        )

    async def handle_archive_upload(
        self, archive_file: UploadFile
    ) -> tuple[str, Path]:
        """
        处理上传的压缩包：保存并自动解压。

        Args:
            archive_file: 上传的压缩包文件

        Returns:
            (task_id, storage_path) 元组

        Raises:
            ValueError: 解压失败
        """
        if not archive_file.filename:
            raise ValueError("压缩包文件名不能为空")

        task_id = self.generate_task_id()
        task_dir = self.create_task_directory(task_id)

        # 保存压缩包
        archive_path = task_dir / archive_file.filename
        with open(archive_path, "wb") as f:
            content = await archive_file.read()
            f.write(content)

        # 解压压缩包到任务目录
        try:
            self.extract_archive(archive_path, task_dir)
            # 解压成功后可以选择删除原压缩包（可选）
            # archive_path.unlink()
        except Exception as e:
            raise ValueError(
                f"解压压缩包 {archive_file.filename} 失败: {str(e)}"
            ) from e

        return task_id, task_dir

    async def handle_uploaded_files(
        self, files: list[UploadFile]
    ) -> tuple[str, Path]:
        """
        处理上传的文件：保存文件，如果是压缩包则自动解压。

        Args:
            files: 上传的文件列表

        Returns:
            (task_id, storage_path) 元组
        """
        task_id = self.generate_task_id()
        task_dir = self.create_task_directory(task_id)

        # 检查是否有压缩包
        archive_files = [
            f for f in files if f.filename and self.is_archive_file(f.filename)
        ]
        regular_files = [
            f for f in files if not (f.filename and self.is_archive_file(f.filename))
        ]

        # 保存非压缩包文件
        if regular_files:
            self.save_uploaded_files(regular_files, task_dir)

        # 处理压缩包：保存并解压
        for archive_file in archive_files:
            if archive_file.filename:
                archive_path = task_dir / archive_file.filename
                # 保存压缩包
                with open(archive_path, "wb") as f:
                    content = await archive_file.read()
                    f.write(content)

                # 解压压缩包到任务目录
                try:
                    self.extract_archive(archive_path, task_dir)
                    # 解压成功后可以选择删除原压缩包（可选）
                    # archive_path.unlink()
                except Exception as e:
                    raise ValueError(
                        f"解压压缩包 {archive_file.filename} 失败: {str(e)}"
                    ) from e

        return task_id, task_dir

