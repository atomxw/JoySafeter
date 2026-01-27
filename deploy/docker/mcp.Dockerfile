# ============================================================================
# MCP 服务镜像 Dockerfile
# 支持可配置的基础镜像源和 pip 镜像源
# ============================================================================

# ----------------------------------------------------------------------------
# 构建参数 (Build Arguments)
# ----------------------------------------------------------------------------
# 基础镜像配置
ARG BASE_IMAGE_REGISTRY="swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/"
ARG UBUNTU_VERSION=24.04

# 镜像源配置
ARG PIP_INDEX_URL=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
ARG UV_INDEX_URL=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
ARG APT_MIRROR=""

# ----------------------------------------------------------------------------
# 基础镜像
# ----------------------------------------------------------------------------
FROM ${BASE_IMAGE_REGISTRY}ubuntu:${UBUNTU_VERSION}

# 重新声明 ARG（FROM 后需要重新声明才能使用）
ARG PIP_INDEX_URL
ARG UV_INDEX_URL
ARG APT_MIRROR

# ----------------------------------------------------------------------------
# 环境变量
# ----------------------------------------------------------------------------
ENV UV_VERSION=0.8.9 \
    UV_INDEX_URL=${UV_INDEX_URL} \
    TZ=Asia/Shanghai \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONIOENCODING=utf-8 \
    NODE_VERSION=20.x \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /export/App

# ----------------------------------------------------------------------------
# 配置 APT 源（可选：如果设置了 APT_MIRROR 则使用镜像源）
# Ubuntu 24.04 使用 deb822 格式的 ubuntu.sources
# ----------------------------------------------------------------------------
RUN if [ -n "$APT_MIRROR" ]; then \
        # Ubuntu 24.04+ (deb822 格式)
        if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \
            sed -i "s|http://archive.ubuntu.com/ubuntu|${APT_MIRROR}|g; \
                    s|http://security.ubuntu.com/ubuntu|${APT_MIRROR}|g; \
                    s|https://archive.ubuntu.com/ubuntu|${APT_MIRROR}|g; \
                    s|https://security.ubuntu.com/ubuntu|${APT_MIRROR}|g" \
                /etc/apt/sources.list.d/ubuntu.sources; \
        fi; \
        # Ubuntu 22.04 及更早版本
        if [ -f /etc/apt/sources.list ]; then \
            sed -i "s|http://archive.ubuntu.com/ubuntu|${APT_MIRROR}|g; \
                    s|http://security.ubuntu.com/ubuntu|${APT_MIRROR}|g" \
                /etc/apt/sources.list; \
        fi; \
    fi

# ----------------------------------------------------------------------------
# 安装系统依赖
# ----------------------------------------------------------------------------
RUN apt-get update && \
    apt-get install -f -y || true && \
    dpkg --configure -a || true && \
    # 基础工具
    apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg wget git unzip openssl \
        netcat-traditional net-tools lsof \
        tzdata locales supervisor bash-completion vim \
    && \
    # Python 环境
    apt-get install -y --no-install-recommends \
        python3 python3-dev python3-venv python3-pip python3-wheel \
    || (apt-get install -f -y && \
        apt-get install -y --no-install-recommends python3-pip python3-wheel) \
    && \
    # C/C++ 编译工具（用于编译 Python 扩展）
    apt-get install -y --no-install-recommends \
        gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev \
    && \
    # Java 17
    apt-get install -y --no-install-recommends openjdk-17-jdk \
    && \
    # Node.js LTS
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION} | bash - && \
    apt-get install -y nodejs \
    && \
    # 配置 locale
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen en_US.UTF-8 \
    && \
    # 配置时区
    ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone \
    && \
    # 使用 bash 作为默认 shell
    ln -sf /bin/bash /bin/sh \
    && \
    # 配置 Java alternatives
    JAVA_HOME=$(find /usr/lib/jvm -name "java-17-openjdk-*" -type d | head -1) && \
    if [ -z "$JAVA_HOME" ]; then echo "Error: Java 17 not found" && exit 1; fi && \
    update-alternatives --install /usr/bin/java java "$JAVA_HOME/bin/java" 1 && \
    update-alternatives --install /usr/bin/javac javac "$JAVA_HOME/bin/javac" 1 && \
    update-alternatives --set java "$JAVA_HOME/bin/java" && \
    update-alternatives --set javac "$JAVA_HOME/bin/javac" && \
    java -version && javac -version \
    && \
    # 清理缓存
    rm -rf /var/lib/apt/lists/* && apt-get clean

# ----------------------------------------------------------------------------
# 配置 Python 包管理器
# ----------------------------------------------------------------------------
RUN mkdir -p /root/.pip && \
    printf '[global]\nindex-url = %s\nbreak-system-packages = true\n' "${PIP_INDEX_URL}" > /root/.pip/pip.conf && \
    pip install --no-cache-dir uv==${UV_VERSION} -i ${PIP_INDEX_URL} --break-system-packages

# ----------------------------------------------------------------------------
# 创建目录结构
# ----------------------------------------------------------------------------
RUN mkdir -p \
    /export/App/supervisor/conf.d \
    /export/App/scripts \
    /export/App/logs \
    /export/App/code \
    /export/App/run

# ----------------------------------------------------------------------------
# 复制配置文件
# ----------------------------------------------------------------------------
COPY deploy/docker/mcp/supervisord.conf /export/App/supervisor/supervisord.conf
COPY deploy/docker/mcp/start.sh /export/App/scripts/start.sh
RUN chmod +x /export/App/scripts/start.sh

# ----------------------------------------------------------------------------
# 复制 MCP 服务器代码和 Supervisor 配置到镜像中
# ----------------------------------------------------------------------------
COPY deploy/docker/mcp/mcp_servers /export/App/code
COPY deploy/docker/mcp/supervisor/conf.d /export/App/supervisor/conf.d

# ----------------------------------------------------------------------------
# 端口 & 健康检查 & 入口点
# ----------------------------------------------------------------------------
# 预留端口 8001-8010 用于 HTTP/SSE MCP 服务
EXPOSE 8001-8010

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD supervisorctl -c /export/App/supervisor/supervisord.conf status || exit 1

ENTRYPOINT ["/export/App/scripts/start.sh"]
