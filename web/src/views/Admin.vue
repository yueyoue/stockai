<template>
  <div class="page-container">
    <h2 class="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">⚙️ 系统管理</h2>

    <el-tabs v-model="activeTab" tab-position="top">
      <!-- AI 模型设置 -->
      <el-tab-pane label="🤖 AI 模型" name="ai">
        <el-card>
          <template #header><span class="font-semibold">AI 模型配置</span></template>
          <el-form label-width="100px" v-loading="loading">
            <el-form-item label="API Key">
              <el-input v-model="form.llm_api_key" type="password" show-password placeholder="输入你的 API Key" />
              <div class="form-tip">当前: {{ settings.llm_api_key_masked || '未配置' }}</div>
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input v-model="form.llm_base_url" placeholder="https://api.deepseek.com" />
              <div class="form-tip">
                <div>API 请求地址，不同服务商不同：</div>
                <div>• DeepSeek: https://api.deepseek.com</div>
                <div>• 通义千问: https://dashscope.aliyuncs.com/compatible-mode/v1</div>
                <div>• OpenAI: https://api.openai.com</div>
              </div>
            </el-form-item>
            <el-form-item label="模型名称">
              <el-input v-model="form.llm_model" placeholder="deepseek-chat" />
              <div class="form-tip">
                <div>使用的模型名称：</div>
                <div>• DeepSeek: deepseek-chat（推荐，性价比高）</div>
                <div>• 通义千问: qwen-plus</div>
                <div>• OpenAI: gpt-4o-mini</div>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings" :loading="saving">保存</el-button>
              <el-button @click="testLLM" :loading="testingLLM">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        <el-alert v-if="llmResult" :type="llmResult.success ? 'success' : 'error'"
          :title="llmResult.message" show-icon class="mt-4" closable />
      </el-tab-pane>

      <!-- 搜索引擎设置 -->
      <el-tab-pane label="🔍 搜索引擎" name="search">
        <el-card>
          <template #header>
            <div>
              <span class="font-semibold">搜索引擎配置</span>
              <div class="text-xs text-gray-400 mt-1">用于全网资讯搜索，配置后可获取更丰富的新闻、研报、公告信息</div>
            </div>
          </template>
          <el-form label-width="100px" v-loading="loading">
            <!-- 博查 -->
            <el-form-item label="博查 API">
              <el-input v-model="form.bocha_api_key" type="password" show-password placeholder="博查搜索 API Key" />
              <div class="form-tip">
                <div><strong>博查搜索</strong> — 国内中文AI搜索API，结果准确、摘要完整</div>
                <div>• 官网: <a href="https://bocha.cn" target="_blank" class="text-blue-500">bocha.cn</a></div>
                <div>• 用途: 搜索 A 股个股新闻、公告、研报、行业资讯</div>
                <div>• 免费额度: 注册即送 100 次/天</div>
                <div>• 当前: {{ settings.bocha_api_key_masked || '未配置' }}</div>
              </div>
            </el-form-item>

            <!-- Tavily -->
            <el-form-item label="Tavily API">
              <el-input v-model="form.tavily_api_key" type="password" show-password placeholder="Tavily API Key" />
              <div class="form-tip">
                <div><strong>Tavily</strong> — 专为 AI/LLM 优化的搜索 API</div>
                <div>• 官网: <a href="https://tavily.com" target="_blank" class="text-blue-500">tavily.com</a></div>
                <div>• 用途: 搜索全球财经新闻、公司动态、市场分析</div>
                <div>• 免费额度: 每月 1000 次请求</div>
                <div>• 当前: {{ settings.tavily_api_key_masked || '未配置' }}</div>
              </div>
            </el-form-item>

            <!-- Brave -->
            <el-form-item label="Brave API">
              <el-input v-model="form.brave_api_key" type="password" show-password placeholder="Brave Search API Key" />
              <div class="form-tip">
                <div><strong>Brave Search</strong> — 隐私优先的独立搜索引擎，索引超 300 亿页面</div>
                <div>• 官网: <a href="https://brave.com/search/api/" target="_blank" class="text-blue-500">brave.com/search/api</a></div>
                <div>• 用途: 搜索英文财经新闻、美股/港股资讯</div>
                <div>• 免费额度: 每月 2000 次请求</div>
                <div>• 当前: {{ settings.brave_api_key_masked || '未配置' }}</div>
              </div>
            </el-form-item>

            <!-- SearXNG -->
            <el-form-item label="SearXNG">
              <el-input v-model="form.searxng_api_key" placeholder="SearXNG 实例地址，如 https://searx.example.com" />
              <div class="form-tip">
                <div><strong>SearXNG</strong> — 开源免费的元搜索引擎，可自建实例</div>
                <div>• 项目: <a href="https://docs.searxng.org/" target="_blank" class="text-blue-500">docs.searxng.org</a></div>
                <div>• 用途: 聚合多个搜索引擎结果，完全免费无限制</div>
                <div>• 填写你的 SearXNG 实例地址即可，无需 API Key</div>
                <div>• 当前: {{ settings.searxng_api_key || '未配置' }}</div>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveSettings" :loading="saving">保存</el-button>
              <el-button @click="testSearch" :loading="testingSearch">测试搜索</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        <el-alert v-if="searchResult" :type="searchResult.success ? 'success' : 'error'"
          :title="searchResult.message" show-icon class="mt-4" closable />
      </el-tab-pane>

      <!-- 爬虫设置 -->
      <el-tab-pane label="🕷️ 爬虫" name="crawler">
        <el-card>
          <template #header><span class="font-semibold">爬虫配置</span></template>
          <el-form label-width="100px" v-loading="loading">
            <el-form-item label="采集间隔">
              <el-input-number v-model="form.crawler_interval" :min="5" :max="120" />
              <span class="ml-2 text-sm text-gray-500">分钟</span>
              <div class="form-tip">研报和资讯的自动采集间隔，建议 30 分钟</div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings" :loading="saving">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 用户管理 -->
      <el-tab-pane label="👥 用户管理" name="users">
        <el-card>
          <template #header><span class="font-semibold">用户列表</span></template>
          <el-table :data="users" stripe size="small">
            <el-table-column prop="user_id" label="ID" width="50" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="role" label="角色" width="80">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">{{ row.role === 'admin' ? '管理员' : '用户' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="70">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button text :type="row.is_active ? 'danger' : 'success'" size="small" @click="toggleUser(row)">
                  {{ row.is_active ? '禁用' : '启用' }}
                </el-button>
                <el-button text type="warning" size="small" @click="resetPassword(row)">重置密码</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../composables/api'

const activeTab = ref('ai')
const loading = ref(false)
const saving = ref(false)
const testingLLM = ref(false)
const testingSearch = ref(false)
const users = ref([])
const llmResult = ref(null)
const searchResult = ref(null)

const settings = ref({})
const form = reactive({
  llm_api_key: '', llm_base_url: 'https://api.deepseek.com', llm_model: 'deepseek-chat',
  bocha_api_key: '', tavily_api_key: '', brave_api_key: '', searxng_api_key: '',
  crawler_interval: 30,
})

onMounted(() => { fetchSettings(); fetchUsers() })

async function fetchSettings() {
  loading.value = true
  try {
    const res = await api.get('/api/settings')
    settings.value = res.data
    Object.assign(form, {
      llm_base_url: res.data.llm_base_url || 'https://api.deepseek.com',
      llm_model: res.data.llm_model || 'deepseek-chat',
      crawler_interval: res.data.crawler_interval || 30,
    })
  } catch {} finally { loading.value = false }
}

async function fetchUsers() {
  try { const res = await api.get('/api/auth/admin/users'); users.value = res.data } catch {}
}

async function saveSettings() {
  saving.value = true
  try {
    const data = {}
    for (const k of ['llm_api_key', 'llm_base_url', 'llm_model', 'bocha_api_key', 'tavily_api_key', 'brave_api_key', 'searxng_api_key', 'crawler_interval']) {
      if (form[k]) data[k] = form[k]
    }
    await api.put('/api/settings', data)
    ElMessage.success('设置已保存')
    await fetchSettings()
  } catch {} finally { saving.value = false }
}

async function testLLM() {
  testingLLM.value = true; llmResult.value = null
  try { llmResult.value = (await api.post('/api/settings/test-llm')).data }
  catch (e) { llmResult.value = { success: false, message: '测试失败' } }
  finally { testingLLM.value = false }
}

async function testSearch() {
  testingSearch.value = true; searchResult.value = null
  try { searchResult.value = (await api.post('/api/settings/test-search')).data }
  catch (e) { searchResult.value = { success: false, message: '测试失败' } }
  finally { testingSearch.value = false }
}

async function toggleUser(user) {
  try {
    await api.put(`/api/auth/admin/users/${user.user_id}`, { is_active: !user.is_active })
    ElMessage.success('操作成功'); await fetchUsers()
  } catch {}
}

async function resetPassword(user) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新密码', '重置密码', { inputPattern: /.{6,}/, inputErrorMessage: '密码至少6位' })
    await api.put(`/api/auth/admin/users/${user.user_id}`, { password: value })
    ElMessage.success('密码已重置')
  } catch {}
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
  line-height: 1.6;
}
.form-tip strong {
  color: #6b7280;
}
a {
  text-decoration: underline;
}
</style>
