# LocalPlay MCP Server

用于本地运行 MCP (Model Context Protocol ) 服务器的项目，实现鼠标控制功能。

## 安装

使用 `uv` 安装依赖：

```bash
uv add "mcp[cli]" pyautogui
```

或者使用 pip：

```bash
pip install "mcp[cli]" pyautogui
```

## 使用方法

### 启动服务器

运行以下命令启动 MCP 开发服务器：

```bash
    "localplay-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/localplay-mcp-server",
        "run",
        "server.py"
      ]
    }
```



### 服务器功能

当前服务器实现了以下鼠标控制功能：

- **移动鼠标**：将鼠标移动到指定坐标位置
- **鼠标点击**：在当前或指定位置执行鼠标点击操作
- **鼠标拖拽**：从一个位置拖拽到另一个位置
- **鼠标滚动**：执行鼠标滚轮滚动操作



### 使用示例

1. 移动鼠标：将鼠标移动到指定坐标，例如 (100, 200)
2. 鼠标点击：在当前位置或指定位置进行点击操作
3. 鼠标拖拽：从起始位置拖拽到目标位置
4. 鼠标滚动：执行向上或向下的滚动操作

