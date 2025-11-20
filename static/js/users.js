// 用户管理页面 JavaScript

let currentPage = 1;
const pageSize = 20;

// 获取角色名称
function getRoleName(role) {
    const roleMap = {
        'super_admin': '超级管理员',
        'admin': '管理员',
        'user': '普通用户'
    };
    return roleMap[role] || role;
}

// 获取操作按钮（根据权限）
function getActionButtons(user) {
    // 从页面获取权限信息（通过隐藏元素或全局变量）
    const canEdit = window.userPermissions?.canEdit || false;
    const canDelete = window.userPermissions?.canDelete || false;
    const currentUserRole = window.userPermissions?.userRole || 'user';
    
    let buttons = '';
    
    // 只有管理员和超级管理员可以编辑
    if (canEdit) {
        buttons += `<button class="btn btn-primary btn-sm" onclick="editUser(${user.id})">编辑</button>`;
    }
    
    // 只有超级管理员可以删除
    if (canDelete) {
        buttons += `<button class="btn btn-danger btn-sm" onclick="deleteUser(${user.id})">删除</button>`;
    }
    
    // 如果没有任何权限，显示"查看"
    if (!canEdit && !canDelete) {
        buttons += `<button class="btn btn-secondary btn-sm" onclick="viewUser(${user.id})">查看</button>`;
    }
    
    return buttons || '<span class="text-muted">无权限</span>';
}

// 查看用户详情（只读）
function viewUser(userId) {
    editUser(userId, true);  // 传入只读模式
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadUsers();
    loadDepartments();
});

// 加载用户列表
async function loadUsers() {
    try {
        const keyword = document.getElementById('searchKeyword')?.value || '';
        const status = document.getElementById('filterStatus')?.value || '';
        const department = document.getElementById('filterDepartment')?.value || '';
        
        let url = `/api/users?page=${currentPage}&page_size=${pageSize}`;
        if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;
        if (status) url += `&status=${status}`;
        if (department) url += `&department=${encodeURIComponent(department)}`;
        
        const response = await apiGet(url);
        
        if (response.success) {
            renderUsersTable(response.data.users);
            renderPagination(response.data.pagination);
        } else {
            showToast('加载用户列表失败: ' + response.message, 'error');
        }
    } catch (error) {
        showToast('加载用户列表失败: ' + error.message, 'error');
        document.getElementById('usersTableBody').innerHTML = 
            '<tr><td colspan="11" class="text-center">加载失败，请刷新重试</td></tr>';
    }
}

// 渲染用户表格
function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="text-center">暂无用户数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>${user.username || '-'}</td>
            <td>${user.real_name || '-'}</td>
            <td>${user.employee_id || '-'}</td>
            <td>${user.department || '-'}</td>
            <td>${user.position || '-'}</td>
            <td>${user.email || '-'}</td>
            <td>${user.phone || '-'}</td>
            <td><span class="role-badge role-${user.role}">${getRoleName(user.role)}</span></td>
            <td><span class="status-badge status-${user.status === 1 ? 'active' : 'inactive'}">${user.status === 1 ? '启用' : '禁用'}</span></td>
            <td>
                <div class="action-buttons">
                    ${getActionButtons(user)}
                </div>
            </td>
        </tr>
    `).join('');
}

// 渲染分页
function renderPagination(pagination) {
    const paginationDiv = document.getElementById('pagination');
    if (!pagination || pagination.total_pages <= 1) {
        paginationDiv.innerHTML = '';
        return;
    }
    
    const { page, total_pages, total } = pagination;
    
    paginationDiv.innerHTML = `
        <button onclick="goToPage(1)" ${page === 1 ? 'disabled' : ''}>首页</button>
        <button onclick="goToPage(${page - 1})" ${page === 1 ? 'disabled' : ''}>上一页</button>
        <span class="page-info">第 ${page} / ${total_pages} 页 (共 ${total} 条)</span>
        <button onclick="goToPage(${page + 1})" ${page === total_pages ? 'disabled' : ''}>下一页</button>
        <button onclick="goToPage(${total_pages})" ${page === total_pages ? 'disabled' : ''}>末页</button>
    `;
}

// 跳转页面
function goToPage(page) {
    currentPage = page;
    loadUsers();
}

// 搜索用户
function searchUsers() {
    currentPage = 1;
    loadUsers();
}

// 加载部门列表（用于筛选）
async function loadDepartments() {
    try {
        const response = await apiGet('/api/users?page_size=1000');
        if (response.success) {
            const departments = [...new Set(response.data.users
                .map(u => u.department)
                .filter(d => d))].sort();
            
            const select = document.getElementById('filterDepartment');
            if (select) {
                select.innerHTML = '<option value="">全部部门</option>' +
                    departments.map(d => `<option value="${d}">${d}</option>`).join('');
            }
        }
    } catch (error) {
        console.error('加载部门列表失败:', error);
    }
}

// 打开用户编辑/创建模态框
async function openUserModal(userId = null, readOnly = false) {
    const modal = document.getElementById('userModal');
    const form = document.getElementById('userForm');
    const modalTitle = document.getElementById('modalTitle');
    const passwordInput = document.getElementById('password');
    const passwordRequired = document.getElementById('passwordRequired');
    const passwordHint = document.getElementById('passwordHint');
    const positionSelect = document.getElementById('position');
    const roleInput = document.getElementById('role');
    
    form.reset();
    document.getElementById('userId').value = '';
    
    // 职位改变时自动更新角色显示
    if (positionSelect) {
        // 移除旧的事件监听器，添加新的
        const newPositionSelect = positionSelect.cloneNode(true);
        positionSelect.parentNode.replaceChild(newPositionSelect, positionSelect);
        
        newPositionSelect.onchange = function() {
            const position = this.value;
            const roleMap = {
                '总经理': '超级管理员',
                '部长': '管理员',
                '员工': '普通用户'
            };
            if (roleInput) {
                roleInput.value = roleMap[position] || '普通用户';
            }
        };
    }
    
    if (userId) {
        // 编辑模式或查看模式
        modalTitle.textContent = readOnly ? '查看用户' : '编辑用户';
        passwordRequired.style.display = 'none';
        passwordInput.required = false;
        passwordHint.style.display = 'block';
        
        try {
            const response = await apiGet(`/api/users/${userId}`);
            if (response.success) {
                const user = response.data;
                document.getElementById('userId').value = user.id;
                document.getElementById('username').value = user.username || '';
                document.getElementById('realName').value = user.real_name || '';
                document.getElementById('employeeId').value = user.employee_id || '';
                document.getElementById('department').value = user.department || '';
                document.getElementById('position').value = user.position || '';
                document.getElementById('email').value = user.email || '';
                document.getElementById('phone').value = user.phone || '';
                // 角色显示（只读，根据职位自动显示）
                const position = user.position || '';
                const roleMap = {
                    '总经理': '超级管理员',
                    '部长': '管理员',
                    '员工': '普通用户'
                };
                document.getElementById('role').value = roleMap[position] || getRoleName(user.role);
                document.getElementById('status').value = user.status || 1;
            }
        } catch (error) {
            showToast('加载用户信息失败: ' + error.message, 'error');
            return;
        }
        
        // 如果是只读模式，禁用所有输入
        if (readOnly) {
            form.querySelectorAll('input, select').forEach(el => {
                el.disabled = true;
            });
            form.querySelector('.form-actions').style.display = 'none';
        } else {
            form.querySelectorAll('input, select').forEach(el => {
                if (el.id !== 'role') {
                    el.disabled = false;
                } else {
                    el.disabled = true;  // 角色字段始终只读
                }
            });
            form.querySelector('.form-actions').style.display = 'flex';
        }
    } else {
        // 创建模式
        modalTitle.textContent = '添加用户';
        passwordRequired.style.display = 'inline';
        passwordInput.required = true;
        passwordHint.style.display = 'none';
        
        // 确保所有输入可用（除了角色字段）
        form.querySelectorAll('input, select').forEach(el => {
            if (el.id !== 'role') {
                el.disabled = false;
            } else {
                el.disabled = true;  // 角色字段始终只读
            }
        });
        form.querySelector('.form-actions').style.display = 'flex';
    }
    
    modal.classList.add('show');
}

// 关闭模态框
function closeUserModal() {
    const modal = document.getElementById('userModal');
    modal.classList.remove('show');
}

// 保存用户
async function saveUser(event) {
    event.preventDefault();
    
    const userId = document.getElementById('userId').value;
    const formData = {
        username: document.getElementById('username').value,
        real_name: document.getElementById('realName').value,
        employee_id: document.getElementById('employeeId').value,
        department: document.getElementById('department').value,
        position: document.getElementById('position').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        // 不再发送role，由后端根据position自动设置
        status: parseInt(document.getElementById('status').value)
    };
    
    // 根据职位自动显示角色名称（仅用于显示）
    const position = formData.position;
    if (position) {
        const roleMap = {
            '总经理': '超级管理员',
            '部长': '管理员',
            '员工': '普通用户'
        };
        document.getElementById('role').value = roleMap[position] || '普通用户';
    }
    
    const password = document.getElementById('password').value;
    if (password) {
        formData.password = password;
    }
    
    try {
        let response;
        if (userId) {
            // 更新用户
            response = await apiPut(`/api/users/${userId}`, formData);
        } else {
            // 创建用户
            if (!password) {
                showToast('创建用户时必须设置密码', 'error');
                return;
            }
            response = await apiPost('/api/users', formData);
        }
        
        if (response.success) {
            showToast(userId ? '用户更新成功' : '用户创建成功', 'success');
            closeUserModal();
            loadUsers();
            loadDepartments(); // 重新加载部门列表
        } else {
            showToast('操作失败: ' + response.message, 'error');
        }
    } catch (error) {
        showToast('操作失败: ' + error.message, 'error');
    }
}

// 编辑用户
async function editUser(userId, readOnly = false) {
    await openUserModal(userId, readOnly);
}

// 删除用户
async function deleteUser(userId) {
    if (!confirm('确定要删除这个用户吗？')) {
        return;
    }
    
    try {
        const response = await apiDelete(`/api/users/${userId}`);
        if (response.success) {
            showToast('用户已删除', 'success');
            loadUsers();
        } else {
            showToast('删除失败: ' + response.message, 'error');
        }
    } catch (error) {
        showToast('删除失败: ' + error.message, 'error');
    }
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modal = document.getElementById('userModal');
    if (event.target === modal) {
        closeUserModal();
    }
}
