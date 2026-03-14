# 红楼梦 RAG 智能问答系统

## 📖 项目简介

这是一个基于 **RAG（检索增强生成）** 技术的红楼梦智能问答系统，结合了 **FAISS 向量数据库** 和 **通义千问大语言模型**，能够为用户提供准确、有依据的红楼梦相关知识问答服务。

系统支持：
- 📚 红楼梦全文检索与问答
- 🤖 AI 驱动的智能问答
- 🌐 Web 界面交互
- 📑 答案来源追溯
- 💬 多轮对话支持

## 🎯 核心功能

### 1. 文档处理
- 自动加载 `documents/` 目录下的所有文本文件
- 智能文本分块（chunk_size=300, overlap=50）
- 支持红楼梦各章回文件

### 2. 向量检索
- 使用 FAISS 构建高效向量索引
- 语义相似度搜索（top-k=10）
- 支持本地嵌入模型（sentence-transformers/all-MiniLM-L6-v2）

### 3. 智能问答
- 基于检索内容生成准确回答
- 提供答案来源追溯
- 自定义提示模板优化回答质量

### 4. Web 交互界面
- 美观的聊天界面
- 实时问答交互
- 显示参考答案来源

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows/Linux/MacOS

### 安装步骤

#### 1. 克隆项目
```bash
cd D:\文章学习\agent_project\readream_RAG_3.13
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置 API 密钥
编辑 `faiss方法.py` 文件，修改以下配置：
```python
api_key: str = "your-api-key-here"  # 替换为你的通义千问 API 密钥
base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
model_name: str = "qwen-plus"
```

#### 4. 准备文档
确保 `documents/` 目录下包含红楼梦章回文件或其他学习文档。

#### 5. 运行系统

##### 方式一：命令行交互
```bash
python faiss方法.py
```

##### 方式二：Web 界面
```bash
python app.py
```
然后在浏览器访问：`http://localhost:5000`

## 📁 项目结构

```
readream_RAG_3.13/
├── documents/              # 文档目录
│   ├── ai_basics.txt      # AI 基础文档
│   ├── machine_learning.txt
│   ├── deep_learning.txt
│   ├── 第一回*.txt        # 红楼梦章回文件
│   └── ...                # 其他章回
├── faiss_index/           # FAISS 向量索引（自动生成）
├── static/                # Web 静态资源
│   ├── css/              # 样式文件
│   └── js/               # JavaScript 文件
├── templates/             # HTML 模板
├── src.py              # 核心 RAG 系统
├── app.py                 # Flask Web 应用
├── requirements.txt       # 依赖包列表
└── README.md             # 项目说明文档
```

## 🔧 技术架构

### 核心技术栈
- **LangChain**: RAG 框架
- **FAISS**: 向量搜索引擎（Facebook AI Similarity Search）
- **Qwen Model**: 通义千问大语言模型
- **Flask**: Web 后端框架
- **Sentence Transformers**: 文本嵌入模型

### 系统架构
```
用户输入 → 问题预处理 → FAISS 检索 → 相关文档片段 
                                          ↓
                                    LLM 生成回答 ← 提示工程
                                          ↓
                                      返回答案 + 来源
```

## 💡 使用示例

### 命令行模式
```
🎓 AI 学习助手已启动！
💡 输入'exit'退出对话

🤔 你的问题：红楼梦的作者是谁？

❓ 问题：红楼梦的作者是谁？
--------------------------------------------------
🤖 回答：《红楼梦》的作者是曹雪芹...

📚 相关学习资料：
   1. 第一回 甄士隐梦幻识通灵 贾雨村风尘怀闺秀.txt
      内容片段：后因曹雪芹于悼红轩中披阅十载，增删五次...
```

### Web 模式
访问 `http://localhost:5000`，在聊天界面中输入问题即可获得智能回答。

## ⚙️ 配置说明

### API 配置
在 `faiss方法.py` 中的 `ChatQwen` 类配置：
- `api_key`: 阿里云 DashScope API 密钥
- `base_url`: API 端点地址
- `model_name`: 使用的模型名称（qwen-plus/qwen-max）

### 检索参数
可调整的参数：
- `chunk_size`: 文本分块大小（默认 300）
- `chunk_overlap`: 分块重叠度（默认 50）
- `search_kwargs.k`: 检索结果数量（默认 10）
- `temperature`: 生成温度（默认 0.1）

## 🎨 自定义扩展

### 添加新文档
只需将新的 `.txt` 文件放入 `documents/` 目录即可。

### 修改提示模板
编辑 `faiss方法.py` 中的 `setup_rag_chain()` 方法，自定义 `template`。

### 更换嵌入模型
修改 `HuggingFaceEmbeddings` 的 `model_name` 参数。

## 📝 常见问题

### Q1: FAISS 索引加载失败？
A: 删除 `faiss_index/` 目录，重新运行程序会自动创建。

### Q2: API 调用错误？
A: 检查 `api_key` 是否正确，网络连接是否正常。

### Q3: 回答质量不佳？
A: 可以调整：
- 增加检索结果数量（k 值）
- 优化提示模板
- 调整文本分块策略

### Q4: 如何重置索引？
A: 删除 `faiss_index/` 文件夹，重启程序会自动重建索引。

## 📊 性能优化建议

1. **首次运行**: 会下载嵌入模型和创建 FAISS 索引，速度较慢
2. **后续运行**: 自动加载已有索引，速度很快
3. **批量查询**: 建议使用 Web 模式，体验更佳
4. **内存优化**: 可根据需要调整 chunk_size 和 k 值

## 🔒 注意事项

- ⚠️ API 密钥请妥善保管，不要上传到公开代码仓库
- ⚠️ 首次运行需要下载模型文件，请确保网络畅通
- ⚠️ 建议使用 Python 虚拟环境管理依赖

## 📄 许可证

本项目仅供学习交流使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请通过 Issue 反馈。

---

**最后更新**: 2026-03-14
**版本**: v1.0.0
