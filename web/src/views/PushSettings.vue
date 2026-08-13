<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">🔔 推送设置</h2>

    <!-- Add push config -->
    <el-card class="mb-6">
      <template #header>
        <span class="font-semibold">添加推送终端</span>
      </template>
      
      <el-form :model="addForm" label-width="100px">
        <el-form-item label="推送渠道">
          <el-select v-model="addForm.push_channel" class="w-full sm:w-64">
            <el-option label="飞书机器人" value="feishu" />
            <el-option label="企业微信" value="wecom" />
            <el-option label="Telegram" value="telegram" />
            <el-option label="邮箱" value="email" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="addForm.push_channel === 'email'" label="邮箱地址">
          <el-input v-model="addForm.email_address" placeholder="your@email.com" />
        </el-form-item>

        <el-form-item v-else label="Webhook">
          <el-input v-model="addForm.webhook_key" :placeholder="getWebhookPlaceholder()" />
        </el-form-item>

        <el-form-item label="推送过滤">
          <el-checkbox-group v-model="addForm.news_types">
            <el-checkbox label="个股资讯">个股资讯</el-checkbox>
            <el-checkbox label="行业资讯">行业资讯</el-checkbox>
            <el-checkbox label="大盘宏观">大盘宏观</el-checkbox>
            <el-checkbox label="公告">公告</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="addPushConfig" :loading="adding">添加</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Push configs -->
    <el-card class="mb-6">
      <template #header>
        <span class="font-semibold">已配置的推送终端</span>
      </template>

      <div v-if="configs.length === 0" class="text-center py-8 text-gray-400">
        还没有配置推送终端
      </div>

      <div v-else>
        <div
          v-for="config in configs"
          :key="config.config_id"
          class="flex items-center justify-between py-4 border-b"
        >
          <div>
            <div class="font-medium">
              <el-icon v-if="config.push_channel === 'feishu'"><ChatDotRound /></el-icon>
              <el-icon v-else-if="config.push_channel === 'wecom'"><OfficeBuilding /></el-icon>
              <el-icon v-else-if="config.push_channel === 'telegram'"><Promotion /></el-icon>
              <el-icon v-else><Message /></el-icon>
              {{ getChannelName(config.push_channel) }}
            </div>
            <div class="text-sm text-gray-500 mt-1">
              {{ config.webhook_key || config.email_address }}
            </div>
          </div>
          
          <div class="flex items-center gap-4">
            <el-switch
              v-model="config.push_switch"
              @change="togglePush(config)"
            />
            <el-button text type="danger" size="small" @click="deletePushConfig(config.config_id)">
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Push history -->
    <el-card>
      <template #header>
        <span class="font-semibold">推送记录</span>
      </template>

      <el-table :data="records" stripe>
        <el-table-column prop="channel" label="渠道" width="100">
          <template #default="{ row }">
            {{ getChannelName(row.channel) }}
          </template>
        </el-table-column>
        <el-table-column prop="content_type" label="类型" width="100" />
        <el-table-column prop="success" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'" size="small">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_msg" label="错误信息" min-width="200" />
        <el-table-column prop="pushed_at" label="时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.pushed_at) }}
          </template>
        </el-table-column>
      </el-table>

      <div class="mt-4 flex justify-center">
        <el-pagination
          v-model:current-page="recordPagination.page"
          :page-size="recordPagination.pageSize"
          :total="recordPagination.total"
          layout="prev, pager, next"
          @current-change="fetchRecords"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../composables/api'

const adding = ref(false)
const configs = ref([])
const records = ref([])
const recordPagination = ref({ page: 1, pageSize: 20, total: 0 })

const addForm = ref({
  push_channel: 'feishu',
  webhook_key: '',
  email_address: '',
  news_types: ['个股资讯', '公告'],
})

onMounted(() => {
  fetchConfigs()
  fetchRecords()
})

async function fetchConfigs() {
  try {
    const res = await api.get('/api/push/config')
    configs.value = res.data
  } catch {}
}

async function fetchRecords() {
  try {
    const res = await api.get('/api/push/records', {
      params: { page: recordPagination.value.page, page_size: recordPagination.value.pageSize },
    })
    records.value = res.data.items
    recordPagination.value.total = res.data.total
  } catch {}
}

async function addPushConfig() {
  adding.value = true
  try {
    const data = {
      push_channel: addForm.value.push_channel,
      webhook_key: addForm.value.webhook_key,
      email_address: addForm.value.email_address,
      push_filter: { news_types: addForm.value.news_types },
    }
    await api.post('/api/push/config', data)
    ElMessage.success('添加成功')
    await fetchConfigs()
  } catch {} finally {
    adding.value = false
  }
}

async function togglePush(config) {
  try {
    await api.put(`/api/push/config/${config.config_id}`, {
      push_switch: config.push_switch,
    })
  } catch {}
}

async function deletePushConfig(configId) {
  try {
    await ElMessageBox.confirm('确定要删除此推送配置吗？')
    await api.delete(`/api/push/config/${configId}`)
    ElMessage.success('已删除')
    await fetchConfigs()
  } catch {}
}

function getChannelName(channel) {
  const map = { feishu: '飞书', wecom: '企业微信', telegram: 'Telegram', email: '邮箱' }
  return map[channel] || channel
}

function getWebhookPlaceholder() {
  const map = {
    feishu: '飞书机器人 Webhook Key',
    wecom: '企业微信机器人 Webhook Key',
    telegram: 'Bot Token:Chat ID',
  }
  return map[addForm.value.push_channel] || ''
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>
