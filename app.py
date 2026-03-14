"""
红楼梦 RAG 智能问答系统 - Web 服务
================================
Flask 后端 API 服务

运行：python app.py
访问：http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

from src import SimpleRAG  # 导入 RAG 系统

app = Flask(__name__)
CORS(app)

# 全局 RAG 系统实例
rag_system = None

def get_rag_system():
    """获取或初始化 RAG 系统（单例模式）"""
    global rag_system
    if rag_system is None:
        print("🔧 正在初始化 RAG 系统...")
        rag_system = SimpleRAG()
        print("✅ RAG 系统初始化完成")
    return rag_system

@app.route('/')
def index():
    """首页"""
    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', now_time=now_time)

@app.route('/api/query', methods=['POST'])
def query():
    """问答 API 接口"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        # 获取 RAG 系统并执行查询
        rag = get_rag_system()
        result = rag.query(question)
        
        if result and 'result' in result:
            answer = result['result']
            source_documents = result.get('source_documents', [])
            
            # 处理资料来源（去重 + 读取完整内容）
            sources = []
            seen_files = set()
            for doc in source_documents:
                source_path = os.path.basename(doc.metadata.get('source', '未知来源'))
                
                if source_path in seen_files:
                    continue
                seen_files.add(source_path)
                
                # 短预览
                short_content = doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content
                
                # 读取完整文件内容
                try:
                    full_content = doc.page_content
                    file_path = doc.metadata.get('source', '')
                    if file_path and os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            full_content = f.read()
                except Exception as e:
                    print(f"读取文件 {source_path} 失败：{e}")
                    full_content = doc.page_content
                
                sources.append({
                    'source': source_path,
                    'content': short_content,
                    'full_content': full_content
                })
            
            return jsonify({
                'success': True,
                'answer': answer,
                'sources': sources,
                'question': question
            })
        else:
            return jsonify({
                'success': False,
                'error': '未能生成回答，请重试'
            }), 500
            
    except Exception as e:
        print(f"❌ 查询错误：{e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'服务器错误：{str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '服务运行正常',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 红楼梦 RAG 智能问答系统 - Web 服务")
    print("="*50)
    
    # 预加载 RAG 系统
    get_rag_system()
    
    print("\n✅ 服务启动成功！")
    print("📱 访问地址：http://localhost:5000")
    print("💡 按 Ctrl+C 停止服务")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
