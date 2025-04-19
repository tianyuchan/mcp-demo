# MCP-Demo

[TOC]

## 准备环境
* 安装 uv
```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

* 准备 Python 环境和依赖
```shell
cd mcp-demo
# 创建 virtual environment 并激活
uv venv
source .venv/bin/activate
# 安装项目依赖
uv sync
```
* 配置 OpenAI SDK 环境变量
```shell
cat <<EOF > .env
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=sk-xxx  # 替换为自己的 API Key
OPENAI_MODEL=qwen-max
EOF
```

## tool-stdio

### Server
MCP Python SDK 中提供以下两种 MCP Server 实现方式：

| 实现方式   | 易用性 | 个性化 |
|------------|--------|--------|
| FastMCP Server    | 高     | 低     |
| Low-Level Server | 低     | 高     |

以下使用 FastMCP server 实现一个数学运算工具的 MCP server：
[src/server/mcp_server_math.py](src/server/mcp_server_math.py)

### Client: GitHub Copilot
以下使用 GitHub Copilot 测试 MCP Server（其他支持 MCP 集成的应用见：[Clients 示例](https://mcp-docs.cn/clients)），具体步骤如下：

1. mcp-demo/.vscode/mcp.json 中添加以下内容：
```json
{
    "servers": {
        "my-mcp-server-math": {
            "type": "stdio",
            "command": "uv",
            "args": [
                "--directory",
                "/Users/cty/python/mcp-demo/src/server/",  # 替换为自己的路径
                "run",
                "mcp_server_math.py"
            ]
        }
    }
}
```
2. Copilot 选择 Agent 模式，可以发现已经检测到 MCP Server。

![config_copilot](resource/image/config_copilot.png)

3. 测试结果：

![tool_stdio_copilot_client](resource/image/tool_stdio_copilot_client.png)


### Client: Python Code
使用 MCP Python SDK 编写代码实现 MCP Client：
[src/client/client.py](src/client/client.py)
然后测试 MCP Server，具体步骤如下：

1. 运行客户端：
```shell
cd mcp-demo
uv run src/client/client.py src/server/mcp_server_math.py
```

2. 测试结果：

![tool_stdio_code_client](resource/image/tool_stdio_code_client.png)


## 参考资料
* https://mcp-docs.cn/introduction
* https://github.com/modelcontextprotocol/python-sdk
* https://blog.csdn.net/GOBinCC/article/details/146290820
