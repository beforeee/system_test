// 用户管理页面 JavaScript

let currentPage = 1;
const pageSize = 20;
const columnDefaultWidths = [70, 120, 110, 110, 110, 110, 210, 140, 110, 90, 170];
const columnWidthStorageKey = 'userTableColumnWidths_v1';
const gradientStorageKey = 'userTableHeaderGradient_v1';
const gradientDefaults = {
    start: '#667eea',
    end: '#764ba2'
};
const minimumColumnWidth = 70;

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
    const canEdit = window.userPermissions?.canEdit || false;
    const canDelete = window.userPermissions?.canDelete || false;
    const canDisable = window.userPermissions?.canDisable || false;
    const currentUserId = window.userPermissions?.currentUserId || null;
    const isActive = Number(user.status) === 1;
    
    let buttons = '';
    
    if (canEdit) {
        buttons += `<button class="btn btn-primary btn-sm" onclick="editUser(${user.id})">编辑</button>`;
    }
    
    if (canDisable && user.id !== currentUserId) {
        if (isActive) {
            buttons += `<button class="btn btn-warning btn-sm" onclick="disableUser(${user.id})">停用</button>`;
        } else {
            buttons += `<button class="btn btn-success btn-sm" onclick="enableUser(${user.id})">启用</button>`;
        }
    }
    
    if (canDelete && user.id !== currentUserId) {
        buttons += `<button class="btn btn-danger btn-sm" onclick="deleteUser(${user.id})">删除</button>`;
    }
    
    if (!buttons) {
        buttons = `<button class="btn btn-secondary btn-sm" onclick="viewUser(${user.id})">查看</button>`;
    }
    
    return buttons;
}

// 查看用户详情（只读）
function viewUser(userId) {
    editUser(userId, true);  // 传入只读模式
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    initTableAppearanceControls();
    initColumnResizing();
    loadUsers();
    loadDepartments();
    loadPositions();
});

// 加载用户列表
async function loadUsers() {
    try {
        const keyword = document.getElementById('searchKeyword')?.value || '';
        const status = document.getElementById('filterStatus')?.value || '';
        const departmentId = document.getElementById('filterDepartment')?.value || '';
        
        let url = `/api/users?page=${currentPage}&page_size=${pageSize}`;
        if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;
        if (status) url += `&status=${status}`;
        if (departmentId) url += `&department_id=${departmentId}`;
        
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
            ${(() => {
                const isActive = Number(user.status) === 1;
                const statusClass = isActive ? 'active' : 'inactive';
                const statusText = isActive ? '启用' : '禁用';
                return `<td><span class="status-badge status-${statusClass}">${statusText}</span></td>`;
            })()}
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

// 加载部门列表（用于筛选和表单）
async function loadDepartments(options = {}) {
    const { refreshFilter = true, refreshForm = true } = options;
    try {
        const response = await apiGet('/api/departments?status=1');
        if (response.success) {
            const departments = response.data || [];
            window.departmentsCache = departments;
            
            if (refreshFilter) {
                const filterSelect = document.getElementById('filterDepartment');
                if (filterSelect) {
                    const previousValue = filterSelect.value;
                    filterSelect.innerHTML = '<option value="">全部部门</option>' +
                        departments.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
                    if (previousValue && filterSelect.querySelector(`option[value="${previousValue}"]`)) {
                        filterSelect.value = previousValue;
                    }
                }
            }
            
            if (refreshForm) {
                const formSelect = document.getElementById('department');
                if (formSelect) {
                    const previousValue = formSelect.value;
                    formSelect.innerHTML = '<option value="">请选择部门</option>' +
                        departments.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
                    if (previousValue && formSelect.querySelector(`option[value="${previousValue}"]`)) {
                        formSelect.value = previousValue;
                    }
                }
            }
        }
    } catch (error) {
        console.error('加载部门列表失败:', error);
    }
}

// 加载职位列表（用于表单）
async function loadPositions(options = {}) {
    const { refreshForm = true } = options;
    try {
        const response = await apiGet('/api/positions?status=1');
        if (response.success && refreshForm) {
            const positions = response.data || [];
            window.positionsCache = positions;
            const positionSelect = document.getElementById('position');
            
            if (positionSelect) {
                const previousValue = positionSelect.value;
                positionSelect.innerHTML = '<option value="">请选择职位</option>' +
                    positions.map(p => `<option value="${p.id}" data-role="${p.role}">${p.name}</option>`).join('');
                if (previousValue && positionSelect.querySelector(`option[value="${previousValue}"]`)) {
                    positionSelect.value = previousValue;
                }
                
                positionSelect.onchange = function() {
                    updateRoleDisplayFromPosition();
                };
            }
        }
        
        // 确保初始化时同步更新角色显示
        updateRoleDisplayFromPosition();
    } catch (error) {
        console.error('加载职位列表失败:', error);
    }
}

function updateRoleDisplayFromPosition() {
    const positionSelect = document.getElementById('position');
    const roleInput = document.getElementById('role');
    if (!positionSelect || !roleInput) return;
    
    const selectedOption = positionSelect.options[positionSelect.selectedIndex];
    if (selectedOption && selectedOption.dataset.role) {
        roleInput.value = getRoleName(selectedOption.dataset.role);
    } else {
        roleInput.value = '普通用户';
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
    
    // 重新加载部门和职位列表（仅刷新表单）
    await loadDepartments({ refreshFilter: false, refreshForm: true });
    await loadPositions({ refreshForm: true });
    
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
                // 使用ID而不是名称
                document.getElementById('department').value = user.department_id || '';
                document.getElementById('position').value = user.position_id || '';
                document.getElementById('email').value = user.email || '';
                document.getElementById('phone').value = user.phone || '';
                document.getElementById('role').value = getRoleName(user.role);
                document.getElementById('status').value = user.status || 1;
                
                if (positionSelect) {
                    positionSelect.dispatchEvent(new Event('change'));
                }
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
    const departmentId = document.getElementById('department').value;
    const positionId = document.getElementById('position').value;
    
    const formData = {
        username: document.getElementById('username').value,
        real_name: document.getElementById('realName').value,
        employee_id: document.getElementById('employeeId').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        status: parseInt(document.getElementById('status').value)
    };
    
    // 使用ID而不是名称
    if (departmentId) {
        formData.department_id = parseInt(departmentId);
    }
    if (positionId) {
        formData.position_id = parseInt(positionId);
    }
    
    // 根据职位自动显示角色名称（仅用于显示）
    if (positionId) {
        const positionSelect = document.getElementById('position');
        const selectedOption = positionSelect.options[positionSelect.selectedIndex];
        if (selectedOption && selectedOption.dataset.role) {
            const roleMap = {
                'super_admin': '超级管理员',
                'admin': '管理员',
                'user': '普通用户'
            };
            document.getElementById('role').value = roleMap[selectedOption.dataset.role] || '普通用户';
        }
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
            loadDepartments(); // 重新加载部门列表（用于筛选）
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
    if (!confirm('确定要彻底删除这个用户吗？此操作不可恢复！')) {
        return;
    }
    
    try {
        const response = await apiDelete(`/api/users/${userId}`);
        if (response.success) {
            showToast('用户已彻底删除', 'success');
            loadUsers();
        } else {
            showToast('删除失败: ' + response.message, 'error');
        }
    } catch (error) {
        showToast('删除失败: ' + error.message, 'error');
    }
}

async function disableUser(userId) {
    if (!confirm('确定要停用这个用户吗？停用后将无法登录系统。')) {
        return;
    }
    
    try {
        const response = await apiPost(`/api/users/${userId}/disable`, {});
        if (response.success) {
            showToast('用户已停用', 'success');
            loadUsers();
        } else {
            showToast('停用失败: ' + response.message, 'error');
        }
    } catch (error) {
        showToast('停用失败: ' + error.message, 'error');
    }
}

async function enableUser(userId) {
    if (!confirm('确定要启用这个用户吗？')) {
        return;
    }
    
    try {
        const response = await apiPost(`/api/users/${userId}/enable`, {});
        if (response.success) {
            showToast('用户已启用', 'success');
            loadUsers();
        } else {
            showToast('启用失败: ' + response.message, 'error');
        }
    } catch (error) {
        showToast('启用失败: ' + error.message, 'error');
    }
}

function initTableAppearanceControls() {
    const startInput = document.getElementById('headerGradientStart');
    const endInput = document.getElementById('headerGradientEnd');
    const resetBtn = document.getElementById('resetTableStyleBtn');
    const panel = document.getElementById('tableStylePanel');
    const toggleBtn = document.getElementById('toggleTableStyleBtn');
    
    if (!startInput || !endInput || !panel || !toggleBtn) {
        return;
    }
    
    toggleBtn.addEventListener('click', () => {
        const willShow = !panel.classList.contains('show');
        panel.classList.toggle('show', willShow);
        toggleBtn.setAttribute('aria-expanded', String(willShow));
    });
    
    document.addEventListener('click', (event) => {
        if (!panel.classList.contains('show')) return;
        if (panel.contains(event.target) || event.target === toggleBtn) return;
        panel.classList.remove('show');
        toggleBtn.setAttribute('aria-expanded', 'false');
    });
    
    const savedGradient = getSavedGradient() || gradientDefaults;
    startInput.value = savedGradient.start;
    endInput.value = savedGradient.end;
    applyHeaderGradient(savedGradient.start, savedGradient.end, false);
    
    startInput.addEventListener('input', () => {
        applyHeaderGradient(startInput.value, endInput.value, true);
    });
    endInput.addEventListener('input', () => {
        applyHeaderGradient(startInput.value, endInput.value, true);
    });
    
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            startInput.value = gradientDefaults.start;
            endInput.value = gradientDefaults.end;
            applyHeaderGradient(gradientDefaults.start, gradientDefaults.end, true);
            resetColumnWidths();
        });
    }
}

function applyHeaderGradient(startColor, endColor, persist = false) {
    document.documentElement.style.setProperty('--table-header-gradient-start', startColor);
    document.documentElement.style.setProperty('--table-header-gradient-end', endColor);
    if (persist) {
        localStorage.setItem(gradientStorageKey, JSON.stringify({ start: startColor, end: endColor }));
    }
}

function getSavedGradient() {
    try {
        const raw = localStorage.getItem(gradientStorageKey);
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        if (parsed?.start && parsed?.end) {
            return parsed;
        }
    } catch (error) {
        console.warn('读取表头渐变配置失败', error);
    }
    return null;
}

function initColumnResizing() {
    const table = document.getElementById('usersTable');
    const colGroup = document.getElementById('userTableColGroup');
    if (!table || !colGroup) return;
    
    const headers = table.querySelectorAll('thead th');
    const savedWidths = getSavedColumnWidths();
    if (savedWidths && savedWidths.length === headers.length) {
        applyColumnWidths(savedWidths);
    } else {
        applyColumnWidths(columnDefaultWidths);
        saveColumnWidths(columnDefaultWidths);
    }
    
    headers.forEach((th, index) => {
        const handle = document.createElement('span');
        handle.className = 'resize-handle';
        handle.dataset.colIndex = index;
        th.appendChild(handle);
    });
    
    let startX = 0;
    let startWidth = 0;
    let targetIndex = null;
    let activeHandle = null;
    
    const onPointerMove = (event) => {
        if (targetIndex === null) return;
        const delta = event.clientX - startX;
        const newWidth = Math.max(minimumColumnWidth, startWidth + delta);
        setColumnWidth(targetIndex, newWidth);
    };
    
    const onPointerUp = () => {
        if (targetIndex === null) return;
        document.removeEventListener('pointermove', onPointerMove);
        document.removeEventListener('pointerup', onPointerUp);
        if (activeHandle) {
            activeHandle.classList.remove('active');
            activeHandle = null;
        }
        targetIndex = null;
        saveColumnWidths();
    };
    
    table.addEventListener('pointerdown', (event) => {
        const handle = event.target.closest('.resize-handle');
        if (!handle) return;
        const colIndex = Number(handle.dataset.colIndex);
        const col = colGroup.children[colIndex];
        if (!col) return;
        event.preventDefault();
        startX = event.clientX;
        startWidth = col.getBoundingClientRect().width;
        targetIndex = colIndex;
        activeHandle = handle;
        handle.classList.add('active');
        document.addEventListener('pointermove', onPointerMove);
        document.addEventListener('pointerup', onPointerUp);
    });
}

function getSavedColumnWidths() {
    try {
        const raw = localStorage.getItem(columnWidthStorageKey);
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : null;
    } catch (error) {
        console.warn('读取列宽配置失败', error);
        return null;
    }
}

function applyColumnWidths(widths) {
    const colGroup = document.getElementById('userTableColGroup');
    if (!colGroup) return;
    Array.from(colGroup.children).forEach((col, index) => {
        const width = widths[index];
        if (width) {
            col.style.width = `${width}px`;
        }
    });
}

function setColumnWidth(index, width) {
    const colGroup = document.getElementById('userTableColGroup');
    if (!colGroup) return;
    const col = colGroup.children[index];
    if (col) {
        col.style.width = `${width}px`;
    }
}

function saveColumnWidths(widthsOverride = null) {
    const colGroup = document.getElementById('userTableColGroup');
    if (!colGroup) return;
    const widths = widthsOverride || Array.from(colGroup.children).map(col => {
        const width = parseFloat(col.style.width);
        return Number.isNaN(width) ? col.getBoundingClientRect().width : width;
    });
    localStorage.setItem(columnWidthStorageKey, JSON.stringify(widths));
}

function resetColumnWidths() {
    applyColumnWidths(columnDefaultWidths);
    saveColumnWidths(columnDefaultWidths);
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modal = document.getElementById('userModal');
    if (event.target === modal) {
        closeUserModal();
    }
}
