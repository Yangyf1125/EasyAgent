# mcp-akshare 项目

将akshare数据接口转换为MCP工具格式的Python项目

## 功能

- 将akshare数据接口转换为标准的MCP工具格式
- 提供统一的API调用方式
- 支持多种金融数据接口

## mcp使用
### 直接使用
```json
{
  "mcpServers": {
    "mcp-akshare": {
      "command": "uvx",
      "args": [
        "mcp-akshare"
      ]
    }
}
```
### 源码使用
```bash
git clone https://github.com/August1996/mcp-akshare.git
```

> 其中mcp-akshare_dir是mcp-akshare项目的路径
```json
{
  "mcpServers": {
    "mcp-akshare": {
      "command": "uvx",
      "args": [
        "mcp-akshare_dir"
      ]
    }
}
```

## 贡献
更多接口参考：https://akshare.akfamily.xyz/data/stock/stock.html
欢迎新增更多实用的数据接口提交Pull Request或Issue



## 许可证

MIT License
