# Docker 构建加速指南

## 问题描述

在使用 Docker Compose 构建镜像时，`apt-get update` 和 `pip install` 下载依赖包速度很慢，特别是在中国大陆地区。

## 解决方案

项目已内置镜像源加速功能，支持通过构建参数灵活配置。

### 1. 使用方式

#### 方式一：通过 docker-compose.yml 配置（推荐）

编辑 `docker-compose.yml`，在 `backend` 服务的 `build` 部分添加 `args`：

```yaml
backend:
  build:
    context: .
    dockerfile: Dockerfile
    args:
      APT_MIRROR: aliyun    # APT镜像源
      PIP_MIRROR: aliyun    # PIP镜像源
```

#### 方式二：通过命令行构建

```bash
# 使用阿里云镜像源
docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun -t emotional_chat_backend .

# 使用清华大学镜像源
docker build --build-arg APT_MIRROR=tsinghua --build-arg PIP_MIRROR=tsinghua -t emotional_chat_backend .

# 不使用镜像源（海外用户）
docker build -t emotional_chat_backend .
```

### 2. 支持的镜像源

#### APT 镜像源（系统依赖）

| 选项 | 说明 | 适用场景 |
|------|------|----------|
| `aliyun` | 阿里云镜像 | 推荐，速度快且稳定 |
| `tsinghua` | 清华大学镜像 | 教育网用户推荐 |
| `ustc` | 中科大镜像 | 备选方案 |
| 留空 | 官方 Debian 源 | 海外用户或网络良好时 |

#### PIP 镜像源（Python 包）

| 选项 | 说明 | 适用场景 |
|------|------|----------|
| `aliyun` | 阿里云镜像 | 推荐，速度快且稳定 |
| `tsinghua` | 清华大学镜像 | 教育网用户推荐 |
| `douban` | 豆瓣镜像 | 备选方案 |
| 留空 | 官方 PyPI 源 | 海外用户或网络良好时 |

### 3. 性能对比

使用镜像源后，构建速度通常可以提升 **5-10 倍**：

- **不使用镜像源**：apt-get update 可能需要 5-10 分钟
- **使用阿里云镜像源**：apt-get update 通常只需 30 秒-1 分钟

### 4. 常见问题

#### Q: 如何验证镜像源是否生效？

A: 构建时查看日志，会显示使用的镜像源：
```
使用阿里云镜像源
```

#### Q: 构建失败怎么办？

A: 可以尝试：
1. 切换到其他镜像源（如从 aliyun 切换到 tsinghua）
2. 不使用镜像源，直接使用官方源
3. 检查网络连接和防火墙设置

#### Q: 海外用户需要配置吗？

A: 不需要。海外用户可以直接使用官方源，速度通常已经很快。只需在 `docker-compose.yml` 中删除或留空 `APT_MIRROR` 和 `PIP_MIRROR` 参数即可。

### 5. 技术实现

Dockerfile 使用多阶段构建，在 builder 阶段：
1. 根据 `APT_MIRROR` 参数替换 Debian 源
2. 根据 `PIP_MIRROR` 参数配置 pip 源
3. 安装系统依赖和 Python 包

这样可以确保：
- 构建速度大幅提升
- 不影响最终镜像大小
- 保持构建的可重复性

### 6. 最佳实践

1. **开发环境**：使用阿里云镜像源（默认配置）
2. **生产环境**：根据实际网络环境选择最稳定的镜像源
3. **CI/CD 环境**：根据构建服务器所在地区选择镜像源
4. **定期更新**：定期检查镜像源可用性，必要时切换
