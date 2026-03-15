"""
红楼梦 RAG 智能问答系统
=====================
基于 FAISS + LangChain + 通义千问的文档问答系统

作者：个人项目
时间：2026-03
版本：v1.0
"""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI

# LangChain 相关导入
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pydantic import Field


class ChatQwen(BaseChatModel):
    """通义千问模型的 LangChain 适配器"""
    
    # 模型配置
    model_name: str = "qwen-plus"
    api_key: str = "YOUR_API_KEY"  # TODO: 替换为你的 API 密钥
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    @property
    def _llm_type(self) -> str:
        return "qwen"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "base_url": self.base_url
        }

    def _generate(
            self,
            messages: List,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        """生成模型回复"""
        # 转换消息格式为 OpenAI 标准格式
        openai_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})

        try:
            # 调用通义千问 API
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url.strip()
            )

            completion = client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                extra_body={"enable_thinking": False},
                stream=False,
                temperature=0.1  # 低温度让输出更确定
            )

            # 构建返回结果
            message = AIMessage(content=completion.choices[0].message.content)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])

        except Exception as e:
            print(f"❌ API 调用错误：{e}")
            error_message = AIMessage(content=f"错误：{str(e)}")
            return ChatResult(generations=[ChatGeneration(message=error_message)])


class SimpleRAG:
    """简单的 RAG（检索增强生成）系统"""
    
    def __init__(self):
        # 初始化组件
        self.llm = ChatQwen()
        self.vector_store = None
        self.documents_dir = "./documents"
        self.faiss_index_path = "./faiss_index"

        # 确保文档目录存在
        os.makedirs(self.documents_dir, exist_ok=True)

    def load_and_process_documents(self):
        """加载并处理文档"""
        documents = []

        # 扫描 documents 目录下的所有 txt 文件
        print(f"📂 正在加载文档：{self.documents_dir}")
        for filename in os.listdir(self.documents_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.documents_dir, filename)
                loader = TextLoader(file_path, encoding='utf-8')
                docs = loader.load()
                documents.extend(docs)

        print(f"✅ 加载了 {len(documents)} 个文档")

        # 文本分割
        text_splitter = CharacterTextSplitter(
            chunk_size=300,      # 每块 300 字符
            chunk_overlap=50,    # 重叠 50 字符
            separator="\n",
            length_function=len,
        )
        texts = text_splitter.split_documents(documents)
        print(f"✅ 分割为 {len(texts)} 个文本块")

        return texts

    def create_vector_store(self):
        """创建 FAISS 向量数据库"""
        texts = self.load_and_process_documents()

        # 使用 sentence-transformers 嵌入模型
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # 加载或创建 FAISS 索引
        if os.path.exists(self.faiss_index_path):
            print("🔄 加载现有的 FAISS 索引...")
            self.vector_store = FAISS.load_local(
                self.faiss_index_path,
                embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            print("🚀 创建新的 FAISS 索引...")
            self.vector_store = FAISS.from_documents(texts, embeddings)
            self.vector_store.save_local(self.faiss_index_path)
            print(f"✅ FAISS 索引已保存到 {self.faiss_index_path}")

        return self.vector_store

    def setup_rag_chain(self):
        """使用 LCEL 构建 RAG 问答链"""
        if not self.vector_store:
            self.create_vector_store()

        # RAG 提示词模板
        template = """
你是一个红楼梦智能问答助手。请基于以下参考资料回答问题。

【参考资料】
{context}

【问题】
{question}

【回答要求】
1. 优先基于参考资料回答
2. 如果资料不足，可以补充你的知识
3. 用中文回答，条理清晰
4. 标注关键信息

【你的回答】
"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # 创建检索器
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}  # 检索 top-10 相关文档
        )

        # ========== LCEL 方式构建 RAG 链 ==========
        def format_docs(docs):
            """将文档格式化为字符串"""
            return "\n\n".join(doc.page_content for doc in docs)
        
        # 链式结构：问题 → 检索 → 格式化 → Prompt → LLM → 输出
        self.rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        print("✅ RAG 链构建完成（LCEL 方式）")

    def query(self, question):
        """执行查询"""
        if not hasattr(self, 'rag_chain'):
            self.setup_rag_chain()

        print(f"\n❓ 问题：{question}")
        print("-" * 50)

        try:
            # 使用 LCEL 调用
            answer = self.rag_chain.invoke(question)

            # 显示回答
            print(f"🤖 回答：{answer}")

            # 显示参考来源
            print("\n📚 参考资料：")
            docs = self.vector_store.similarity_search(question, k=10)
            for i, doc in enumerate(docs, 1):
                source = os.path.basename(doc.metadata["source"])
                print(f"   {i}. {source}")
                print(f"      片段：{doc.page_content[:100]}...")

            return {
                'result': answer,
                'source_documents': docs
            }
        except Exception as e:
            print(f"❌ 查询错误：{e}")
            return None

    def interactive_chat(self):
        """交互式对话模式"""
        print("\n" + "="*50)
        print("🎓 红楼梦 RAG 智能问答系统")
        print("💡 输入 'exit' 退出对话")
        print("="*50)

        # 初始化 RAG 链
        if not hasattr(self, 'rag_chain'):
            self.setup_rag_chain()

        while True:
            try:
                question = input("\n🤔 你的问题：").strip()
                
                # 退出条件
                if question.lower() in ['exit', 'quit', 'bye']:
                    print("👋 再见！")
                    break

                if not question:
                    continue

                # 执行查询
                self.query(question)
                print("\n" + "="*50)

            except KeyboardInterrupt:
                print("\n👋 程序已中断")
                break
            except Exception as e:
                print(f"❌ 发生错误：{e}")


# 主程序入口
if __name__ == "__main__":
    # 创建 RAG 系统
    rag_system = SimpleRAG()

    # 启动交互式对话
    rag_system.interactive_chat()
