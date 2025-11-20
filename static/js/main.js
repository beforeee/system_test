// 通用工具函数

// 使用相对路径，自动使用当前页面的协议、域名和端口
const API_BASE_URL = '';

// 显示消息提示
function showToast(message, type = 'info') {
    const toast = document.getElementById('messageToast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// API 请求封装
async function apiRequest(url, options = {}) {
    try {
        const fullUrl = `${API_BASE_URL}${url}`;
        const response = await fetch(fullUrl, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        // 检查响应是否成功
        if (!response.ok) {
            let errorMessage = '请求失败';
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || `HTTP ${response.status}: ${response.statusText}`;
            } catch (e) {
                errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }
        
        // 尝试解析 JSON 响应
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            return data;
        } else {
            // 如果不是 JSON，返回文本
            return { success: true, data: await response.text() };
        }
    } catch (error) {
        // 网络错误或其他错误
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            console.error('API请求错误: 网络连接失败，请检查服务器是否运行', error);
            throw new Error('无法连接到服务器，请检查网络连接或服务器是否正常运行');
        } else {
            console.error('API请求错误:', error);
            throw error;
        }
    }
}

// GET 请求
async function apiGet(url) {
    return apiRequest(url, { method: 'GET' });
}

// POST 请求
async function apiPost(url, data) {
    return apiRequest(url, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// PUT 请求
async function apiPut(url, data) {
    return apiRequest(url, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

// DELETE 请求
async function apiDelete(url) {
    return apiRequest(url, { method: 'DELETE' });
}
