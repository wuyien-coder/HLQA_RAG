// 全局变量
let isProcessing = false;

// DOM 元素
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const messagesContainer = document.getElementById('messagesContainer');
const sourcesList = document.getElementById('sourcesList');
const loadingOverlay = document.getElementById('loadingOverlay');
const fileModal = document.getElementById('fileModal');
const modalTitle = document.getElementById('modalTitle');
const fileContent = document.getElementById('fileContent');
const closeModal = document.getElementById('closeModal');

// 存储所有源文件内容
let sourceFilesData = {};

// 获取当前时间
function getCurrentTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// 添加消息到聊天界面
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = isUser ? '👤' : '🤖';
    
    const content = document.createElement('div');
    content.className = 'content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'text';
    textDiv.textContent = text;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'time';
    timeDiv.textContent = getCurrentTime();
    
    content.appendChild(textDiv);
    content.appendChild(timeDiv);
    
    if (!isUser) {
        messageDiv.appendChild(avatar);
    }
    messageDiv.appendChild(content);
    
    messagesContainer.appendChild(messageDiv);
    
    // 滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 更新资料来源
function updateSources(sources) {
    if (!sources || sources.length === 0) {
        sourcesList.innerHTML = '<p class="empty-tip">暂无参考资料</p>';
        return;
    }
    
    sourcesList.innerHTML = '';
    
    sources.forEach((source, index) => {
        const sourceItem = document.createElement('div');
        sourceItem.className = 'source-item';
        
        const sourceTitle = document.createElement('div');
        sourceTitle.className = 'source-title';
        sourceTitle.textContent = `${index + 1}. ${source.source}`;
        
        const sourceContent = document.createElement('div');
        sourceContent.className = 'source-content';
        sourceContent.textContent = source.content;
        
        const viewBtn = document.createElement('button');
        viewBtn.className = 'view-detail-btn';
        viewBtn.textContent = '👁️ 查看详情';
        viewBtn.onclick = () => viewFileDetail(source.source, source.full_content || source.content);
        
        sourceItem.appendChild(sourceTitle);
        sourceItem.appendChild(sourceContent);
        sourceItem.appendChild(viewBtn);
        sourcesList.appendChild(sourceItem);
        
        // 存储文件内容
        sourceFilesData[source.source] = source.full_content || source.content;
    });
}

// 查看文件详情
function viewFileDetail(filename, content) {
    modalTitle.textContent = '📄 ' + filename;
    fileContent.textContent = content;
    fileModal.classList.add('active');
    document.body.style.overflow = 'hidden'; // 防止背景滚动
}

// 关闭模态框
function hideFileModal() {
    fileModal.classList.remove('active');
    document.body.style.overflow = 'auto'; // 恢复背景滚动
}

// 模态框事件监听
if (closeModal) {
    closeModal.addEventListener('click', hideFileModal);
}

// 点击模态框外部关闭
if (fileModal) {
    fileModal.addEventListener('click', (e) => {
        if (e.target === fileModal) {
            hideFileModal();
        }
    });
}

// ESC 键关闭模态框
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && fileModal.classList.contains('active')) {
        hideFileModal();
    }
});

// 发送问题
async function sendQuestion() {
    const question = questionInput.value.trim();
    
    if (!question || isProcessing) {
        return;
    }
    
    // 显示用户问题
    addMessage(question, true);
    questionInput.value = '';
    
    // 显示加载动画
    isProcessing = true;
    sendBtn.disabled = true;
    loadingOverlay.classList.add('active');
    
    try {
        // 调用后端 API
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 隐藏加载动画
        loadingOverlay.classList.remove('active');
        
        // 显示 AI 回答
        if (data.answer) {
            addMessage(data.answer, false);
            
            // 更新资料来源
            if (data.sources && data.sources.length > 0) {
                updateSources(data.sources);
            } else {
                updateSources([]);
            }
        } else {
            addMessage('抱歉，未能生成回答，请重试。', false);
        }
        
    } catch (error) {
        console.error('Error:', error);
        loadingOverlay.classList.remove('active');
        addMessage(`发生错误：${error.message}，请稍后重试。`, false);
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        questionInput.focus();
    }
}

// 事件监听
sendBtn.addEventListener('click', sendQuestion);

questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuestion();
    }
});

// 页面加载完成后聚焦输入框
window.addEventListener('load', () => {
    questionInput.focus();
});

// 自动调整文本框高度
questionInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    
    // 限制最大高度
    if (this.scrollHeight > 150) {
        this.style.overflowY = 'auto';
    } else {
        this.style.overflowY = 'hidden';
    }
});
