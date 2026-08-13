<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">⚙️ 系统管理</h2>

    <el-tabs v-model="activeTab">
      <!-- 系统设置 -->
      <el-tab-pane label="系统设置" name="settings">
        <el-card>
          <template #header><span class="font-semibold">🤖 AI 模型配置</span></template>
          <el-form label-width="120px" v-loading="settingsLoading">
            <el-form-item label="API Key">
              <el-input 
                v-model="settings.llm_api_key" 
                type="password" 
                show-password
                placeholder="DeepSeek / 通义千问 / Claude API Key"
              />
              <div class="text-xs text-gray-400 mt-1">
                当前: {{ settings.llm_api_key_masked || '未配置' }}
              </div>
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input v-model="settings.llm_base_url" placeholder="https://api.deepseek.com" />
              <div class="text-xs text-gray-400 mt-1">
                DeepSeek: https://api.deepseek.com | 通义千问: https://dashscope.aliyuncs.com/compatible-mode/v1
              </div>
            </el-form-item>
            <el-form-item label="模型名称">
              <el-input v-model="settings.llm_model" placeholder="deepseek-chat" />
              <div class="text-xs text-gray-400 mt-1">
                DeepSeek: deepseek-chat | 通义千问: qwen-plus | GPT: gpt-4o-mini
              </div>
            </el-form-item>
            <el-form-item label="采集间隔">
              <el-input-number v-model="settings.crawler_interval" :min="5" :max="120" />
              <span class="ml-2 text-sm text-gray-500">分钟</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings" :loading="saving">保存设置</el-button>
              <el-button @click="testLLM" :loading="testing">测试 AI 连接</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 测试结果 -->
        <el-card class="mt-4" v-if="testResult">
          <template #header><span class="font-semibold">🧪 连接测试结果</span></template>
          <el-alert
            :type="testResult.success ? 'success' : 'error'"
            :title="testResult.message"
            show-icon
          />
        </el-card>
      </el-tab-pane>

      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <el-card>
          <template #header><span class="font-semibold">👥 用户列表</span></template>
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
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../composables/api'

const activeTab = ref('settings')
const settingsLoading = ref(false)
const saving = ref(false)
const testing = ref(false)
const users = ref([])
const testResult = ref(null)

const settings = ref({
  llm_api_key: '',
  llm_api_key_masked: '',
  llm_base_url: 'https://api.deepseek.com',
  llm_model: 'deepseek-chat',
  crawler_interval: 30,
  push_enabled: true,
})

onMounted(() => {
  fetchSettings()
  fetchUsers()
})

async function fetchSettings() {
  settingsLoading.value = true
  try {
    const res = await api.get('/api/settings')
    settings.value = res.data
  } catch {} finally {
    settingsLoading.value = false
  }
}

async function fetchUsers() {
  try {
    const res = await api.get('/api/auth/admin/users')
    users.value = res.data
  } catch {}
}

async function saveSettings() {
  saving.value = true
  try {
    const data = {}
    if (settings.value.llm_api_key) data.llm_api_key = settings.value.llm_api_key
    if (settings.value.llm_base_url) data.llm_base_url = settings.value.llm_base_url
    if (settings.value.llm_model) data.llm_model = settings.value.llm_model
    if (settings.value.crawler_interval) data.crawler_interval = settings.value.crawler_interval
    
    await api.put('/api/settings', data)
    ElMessage.success('设置已保存')
    await fetchSettings()
  } catch {} finally {
    saving.value = false
  }
}

async function testLLM() {
  testing.value = true
  testResult.value = null
  try {
    const res = await api.post('/api/settings/test-llm')
    testResult.value = res.data
  } catch (e) {
    testResult.value = { success: false, message: '测试失败: ' + (e.response?.data?.detail || e.message) }
  } finally {
    testing.value = false
  }
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

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>
