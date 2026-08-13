<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">📊 大盘复盘仪表盘</h2>

    <!-- 主要指数 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <el-card v-for="(idx, name) in market.indices" :key="name" class="hover-card" shadow="hover">
        <div class="text-center">
          <div class="text-sm text-gray-500">{{ name }}</div>
          <div class="text-2xl font-bold mt-1" :class="idx.change_pct > 0 ? 'text-red-600' : 'text-green-600'">
            {{ idx.price?.toFixed(2) }}
          </div>
          <div class="text-sm" :class="idx.change_pct > 0 ? 'text-red-600' : 'text-green-600'">
            {{ idx.change_pct > 0 ? '+' : '' }}{{ idx.change_pct?.toFixed(2) }}%
          </div>
        </div>
      </el-card>
    </div>

    <!-- 市场统计 -->
    <el-card class="mb-6" v-if="market.stats">
      <template #header><span class="font-semibold">📊 市场统计</span></template>
      <div class="grid grid-cols-2 lg:grid-cols-5 gap-4 text-center">
        <div>
          <div class="text-2xl font-bold text-red-600">{{ market.stats.up_count || 0 }}</div>
          <div class="text-sm text-gray-500">上涨</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-green-600">{{ market.stats.down_count || 0 }}</div>
          <div class="text-sm text-gray-500">下跌</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-gray-600">{{ market.stats.flat_count || 0 }}</div>
          <div class="text-sm text-gray-500">平盘</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-red-600">{{ market.stats.limit_up || 0 }}</div>
          <div class="text-sm text-gray-500">涨停</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-green-600">{{ market.stats.limit_down || 0 }}</div>
          <div class="text-sm text-gray-500">跌停</div>
        </div>
      </div>
    </el-card>

    <!-- AI 大盘分析 -->
    <el-card v-if="market.markdown">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">🤖 AI 大盘分析</span>
          <el-button size="small" @click="copyMarkdown">复制</el-button>
        </div>
      </template>
      <div class="markdown-body" v-html="renderMarkdown(market.markdown)"></div>
    </el-card>

    <!-- 自选股看板 -->
    <el-card class="mt-6">
      <template #header><span class="font-semibold">⭐ 自选股看板</span></template>
      <div v-if="watchlistDashboard.stocks?.length === 0" class="text-center py-8 text-gray-400">
        暂无自选股，去添加吧！
      </div>
      <div v-else class="space-y-3">
        <div v-for="stock in watchlistDashboard.stocks" :key="stock.code"
          class="flex items-center justify-between p-4 rounded-lg border hover:shadow-md cursor-pointer transition-shadow"
          @click="goToDetail(stock)">
          <div class="flex items-center gap-4">
            <span class="text-2xl">{{ stock.signal_icon }}</span>
            <div>
              <div class="font-bold">{{ stock.name }}</div>
              <div class="text-sm text-gray-400">{{ stock.code }}</div>
            </div>
          </div>
          <div class="text-right">
            <div class="text-lg font-bold" :class="stock.change_pct > 0 ? 'text-red-600' : 'text-green-600'">
              {{ stock.price?.toFixed(2) || '--' }}
            </div>
            <div class="text-sm" :class="stock.change_pct > 0 ? 'text-red-600' : 'text-green-600'">
              {{ stock.change_pct > 0 ? '+' : '' }}{{ stock.change_pct?.toFixed(2) || '0' }}%
            </div>
          </div>
          <div class="text-right hidden sm:block">
            <el-tag :type="getScoreType(stock.score)" size="small">
              {{ stock.score }}/100
            </el-tag>
            <div class="text-xs text-gray-400 mt-1">{{ stock.signal }}</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../composables/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const market = ref({})
const watchlistDashboard = ref({})

onMounted(() => {
  fetchMarket()
  fetchWatchlistDashboard()
})

async function fetchMarket() {
  try {
    const res = await api.get('/api/dashboard/market')
    market.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function fetchWatchlistDashboard() {
  try {
    const res = await api.get('/api/dashboard/watchlist')
    watchlistDashboard.value = res.data
  } catch (e) {
    console.error(e)
  }
}

function goToDetail(stock) {
  router.push({ path: `/stock/${stock.code}`, query: { name: stock.name } })
}

function getScoreType(score) {
  if (score >= 70) return 'danger'
  if (score >= 50) return 'warning'
  return 'success'
}

function renderMarkdown(md) {
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/\n/g, '<br>')
}

function copyMarkdown() {
  navigator.clipboard.writeText(market.value.markdown)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.markdown-body { font-size: 14px; line-height: 1.8; }
.markdown-body h1 { font-size: 20px; font-weight: bold; margin: 16px 0 8px; }
.markdown-body h2 { font-size: 18px; font-weight: bold; margin: 14px 0 6px; }
.markdown-body strong { color: #1f2937; }
.markdown-body li { margin-left: 16px; list-style: disc; }
</style>
