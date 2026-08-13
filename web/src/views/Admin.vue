<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">⚙️ 系统管理</h2>

    <!-- System config -->
    <el-card class="mb-6">
      <template #header>
        <span class="font-semibold">系统配置</span>
      </template>
      
      <el-form label-width="120px">
        <el-form-item label="AI API Key">
          <el-input v-model="config.llm_api_key" type="password" show-password placeholder="DeepSeek / 通义千问 API Key" />
        </el-form-item>
        <el-form-item label="AI Base URL">
          <el-input v-model="config.llm_base_url" placeholder="https://api.deepseek.com" />
        </el-form-item>
        <el-form-item label="AI 模型">
          <el-input v-model="config.llm_model" placeholder="deepseek-chat" />
        </el-form-item>
        <el-form-item label="采集间隔(分钟)">
          <el-input-number v-model="config.crawler_interval" :min="5" :max="120" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- User management -->
    <el-card class="mb-6">
      <template #header>
        <span class="font-semibold">用户管理</span>
      </template>

      <el-table :data="users" stripe>
        <el-table-column prop="user_id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              text
              :type="row.is_active ? 'danger' : 'success'"
              size="small"
              @click="toggleUser(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button
              text
              type="warning"
              size="small"
              @click="resetPassword(row)"
            >
              重置密码
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../composables/api'

const users = ref([])
const config = ref({
  llm_api_key: '',
  llm_base_url: '',
  llm_model: 'deepseek-chat',
  crawler_interval: 30,
})

onMounted(() => {
  fetchUsers()
})

async function fetchUsers() {
  try {
    const res = await api.get('/api/auth/admin/users')
    users.value = res.data
  } catch {}
}

async function toggleUser(user) {
  try {
    await api.put(`/api/auth/admin/users/${user.user_id}`, {
      is_active: !user.is_active,
    })
    ElMessage.success('操作成功')
    await fetchUsers()
  } catch {}
}

async function resetPassword(user) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新密码', '重置密码', {
      inputPattern: /.{6,}/,
      inputErrorMessage: '密码至少6位',
    })
    await api.put(`/api/auth/admin/users/${user.user_id}`, {
      password: value,
    })
    ElMessage.success('密码已重置')
  } catch {}
}

async function saveConfig() {
  // TODO: Implement config save via API
  ElMessage.success('配置保存成功')
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>
