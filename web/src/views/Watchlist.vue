<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">⭐ 我的自选</h2>

    <!-- 搜索添加 -->
    <el-card class="mb-6">
      <div class="flex flex-wrap gap-4 items-end">
        <div class="flex-1 min-w-[200px]">
          <div class="text-sm text-gray-500 mb-1">搜索股票（输入代码/名称/拼音）</div>
          <el-autocomplete
            v-model="searchKeyword"
            :fetch-suggestions="querySearch"
            placeholder="如 600519 / 贵州茅台 / GZMT"
            :trigger-on-focus="false"
            @select="handleSelect"
            clearable
            class="w-full"
          >
            <template #default="{ item }">
              <div class="flex items-center justify-between">
                <span class="font-medium">{{ item.name }}</span>
                <span class="text-gray-400 text-sm">{{ item.code }}</span>
              </div>
            </template>
          </el-autocomplete>
        </div>
        <el-button type="primary" @click="addStock" :loading="adding" :disabled="!selectedStock">
          <el-icon><Plus /></el-icon> 添加自选
        </el-button>
      </div>
    </el-card>

    <!-- 自选股列表 -->
    <el-card>
      <div v-if="loading" class="text-center py-12">
        <el-icon class="is-loading text-2xl"><Loading /></el-icon>
      </div>
      
      <div v-else-if="watchlist.length === 0" class="text-center py-12 text-gray-400">
        还没有添加自选股，快去搜索添加吧！
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="stock in watchlist"
          :key="stock.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          @click="viewStockDetail(stock)"
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
            <el-button text type="danger" size="small" @click.stop="removeStock(stock.stock_code)">
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../composables/api'

const router = useRouter()
const loading = ref(false)
const adding = ref(false)
const watchlist = ref([])
const searchKeyword = ref('')
const selectedStock = ref(null)
let searchTimer = null

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

async function querySearch(queryString, cb) {
  if (!queryString || queryString.length < 1) {
    cb([])
    return
  }
  
  try {
    const res = await api.get('/api/watchlist/search', { params: { q: queryString, limit: 10 } })
    const results = res.data.results.map(item => ({
      value: `${item.name} (${item.code})`,
      code: item.code,
      name: item.name,
      market: item.market || 'A股',
    }))
    cb(results)
  } catch {
    cb([])
  }
}

function handleSelect(item) {
  selectedStock.value = item
}

async function addStock() {
  if (!selectedStock.value) {
    ElMessage.warning('请先搜索并选择股票')
    return
  }
  
  adding.value = true
  try {
    await api.post('/api/watchlist', {
      stock_code: selectedStock.value.code,
      stock_name: selectedStock.value.name,
      market_type: selectedStock.value.market,
    })
    ElMessage.success(`${selectedStock.value.name} 已添加到自选`)
    searchKeyword.value = ''
    selectedStock.value = null
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

function viewStockDetail(stock) {
  router.push({ path: `/stock/${stock.stock_code}`, query: { name: stock.stock_name } })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>
