<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">⭐ 我的自选</h2>

    <!-- Add stock -->
    <el-card class="mb-6">
      <div class="flex flex-wrap gap-4 items-end">
        <div>
          <div class="text-sm text-gray-500 mb-1">股票代码</div>
          <el-input v-model="addForm.stock_code" placeholder="如 600519" class="w-32" />
        </div>
        <div>
          <div class="text-sm text-gray-500 mb-1">股票名称</div>
          <el-input v-model="addForm.stock_name" placeholder="如 贵州茅台" class="w-32" />
        </div>
        <div>
          <div class="text-sm text-gray-500 mb-1">市场</div>
          <el-select v-model="addForm.market_type" class="w-24">
            <el-option label="A股" value="A股" />
            <el-option label="港股" value="港股" />
            <el-option label="美股" value="美股" />
          </el-select>
        </div>
        <el-button type="primary" @click="addStock" :loading="adding">
          <el-icon><Plus /></el-icon> 添加
        </el-button>
      </div>
    </el-card>

    <!-- Watchlist -->
    <el-card>
      <div v-if="loading" class="text-center py-12">
        <el-icon class="is-loading text-2xl"><Loading /></el-icon>
      </div>
      
      <div v-else-if="watchlist.length === 0" class="text-center py-12 text-gray-400">
        还没有添加自选股，快去添加吧！
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="stock in watchlist"
          :key="stock.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-center justify-between mb-2">
            <div>
              <div class="font-bold text-lg">{{ stock.stock_name }}</div>
              <div class="text-sm text-gray-500">{{ stock.stock_code }}</div>
            </div>
            <el-tag size="small">{{ stock.market_type }}</el-tag>
          </div>
          
          <div class="flex items-center justify-between mt-4">
            <span class="text-xs text-gray-400">
              添加于 {{ formatDate(stock.add_time) }}
            </span>
            <div class="flex gap-2">
              <el-button text type="primary" size="small" @click="viewStockDetail(stock)">
                详情
              </el-button>
              <el-button text type="danger" size="small" @click="removeStock(stock.stock_code)">
                删除
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Stock detail dialog -->
    <el-dialog v-model="detailVisible" :title="`${selectedStock?.stock_name} (${selectedStock?.stock_code})`" width="800px" top="5vh">
      <el-tabs v-model="detailTab">
        <el-tab-pane label="关联资讯" name="news">
          <div v-if="stockNews.length === 0" class="text-center py-8 text-gray-400">暂无相关资讯</div>
          <div v-for="news in stockNews" :key="news.news_id" class="py-3 border-b">
            <div class="font-medium text-sm">{{ news.title }}</div>
            <div class="flex items-center gap-2 mt-1">
              <el-tag v-if="news.sentiment" size="small" :type="getSentimentType(news.sentiment)">
                {{ news.sentiment }}
              </el-tag>
              <span class="text-xs text-gray-400">{{ formatDateTime(news.publish_time) }}</span>
            </div>
            <div v-if="news.ai_impact" class="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
              {{ news.ai_impact }}
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="关联研报" name="reports">
          <div v-if="stockReports.length === 0" class="text-center py-8 text-gray-400">暂无相关研报</div>
          <div v-for="report in stockReports" :key="report.report_id" class="py-3 border-b">
            <div class="font-medium text-sm">{{ report.title }}</div>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-xs text-gray-400">{{ report.source }}</span>
              <span class="text-xs text-gray-400">{{ formatDateTime(report.publish_time) }}</span>
            </div>
            <div v-if="report.ai_summary" class="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
              {{ report.ai_summary }}
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../composables/api'

const loading = ref(false)
const adding = ref(false)
const watchlist = ref([])
const addForm = ref({ stock_code: '', stock_name: '', market_type: 'A股' })
const detailVisible = ref(false)
const detailTab = ref('news')
const selectedStock = ref(null)
const stockNews = ref([])
const stockReports = ref([])

onMounted(() => fetchWatchlist())

async function fetchWatchlist() {
  loading.value = true
  try {
    const res = await api.get('/api/watchlist')
    watchlist.value = res.data
  } catch {} finally {
    loading.value = false
  }
}

async function addStock() {
  if (!addForm.value.stock_code || !addForm.value.stock_name) {
    ElMessage.warning('请填写股票代码和名称')
    return
  }
  adding.value = true
  try {
    await api.post('/api/watchlist', addForm.value)
    ElMessage.success('添加成功')
    addForm.value = { stock_code: '', stock_name: '', market_type: 'A股' }
    await fetchWatchlist()
  } catch {} finally {
    adding.value = false
  }
}

async function removeStock(stockCode) {
  try {
    await ElMessageBox.confirm('确定要从自选列表移除吗？', '提示')
    await api.delete(`/api/watchlist/${stockCode}`)
    ElMessage.success('已移除')
    await fetchWatchlist()
  } catch {}
}

async function viewStockDetail(stock) {
  selectedStock.value = stock
  detailTab.value = 'news'
  detailVisible.value = true
  
  try {
    const [newsRes, reportsRes] = await Promise.all([
      api.get(`/api/watchlist/${stock.stock_code}/news`),
      api.get(`/api/watchlist/${stock.stock_code}/reports`),
    ])
    stockNews.value = newsRes.data
    stockReports.value = reportsRes.data
  } catch {}
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

function getSentimentType(sentiment) {
  if (sentiment === '利好') return 'success'
  if (sentiment === '利空') return 'danger'
  return 'info'
}
</script>
