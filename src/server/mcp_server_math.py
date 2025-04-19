"""
File   : mcp_server_math.py
Desc   : 数学运算工具（Stdio, Tools, FastMCP）
Date   : 2025/04/15
Author : Tianyu Chen
"""
import numpy as np
from mcp.server.fastmcp import FastMCP


# 初始化 FastMCP server
mcp = FastMCP("math_tools")


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """指数运算：计算 base 的 exponent 次方

    Args:
        base: 底数
        exponent: 次数
    """
    result = base ** exponent
    return {
        "result": result
    }


@mcp.tool()
def logarithm(base: float, value: float) -> float:
    """对数运算：计算以 base 为底的 value 的对数

    Args:
        base: 底数
        value: 值
    """
    if base <= 0 or base == 1 or value <= 0:
        raise ValueError("Base must be greater than 0 and not equal to 1, and value must be greater than 0.")
    result = np.log(value) / np.log(base)
    return {
        "result": result
    }


if __name__ == "__main__":
    # 初始化并运行 server
    mcp.run(transport='stdio')
