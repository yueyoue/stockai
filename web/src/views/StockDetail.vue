<template>
  <div class="stock-detail" v-loading="loading">
    <!-- 头部基础标识区 -->
    <div class="header-card">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 class="text-2xl font-bold">
            {{ dashboard.name }} <span class="text-gray-400 text-lg">({{ dashboard.code }})</span>
          </h2>
          <div class="flex items-center gap-3 mt-2">
            <span class="text-4xl font-bold" :class="priceColor">
              {{ dashboard.quote?.price?.toFixed(2) || '--' }}
            </span>
            <span class="text-lg" :class="priceColor">
              {{ dashboard.quote?.change_pct > 0 ? '+' : '' }}{{ dashboard.quote?.change_pct?.toFixed(2) || '0' }}%
            </span>
          </div>
        </div>
        <div class="text-right">
          <div class="flex items-center gap-2">
            <span class="text-3xl">{{ dashboard.signal_icon }}</span>
            <span class="text-xl font-bold">{{ dashboard.signal }}</span>
          </div>
          <div class="mt-2">
            <span class="inline-block px-3 py-1 rounded-full text-sm font-medium"
              :class="sentimentClass">
              {{ dashboard.score }}/100 {{ dashboard.sentiment }}
            </span>
          </div>
          <div class="text-sm text-gray-500 mt-2">{{ dashboard.conclusion }}</div>
        </div>
      </div>
    </div>

    <!-- 操作建议 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
      <el-card>
        <template #header><span class="font-semibold">🟢 持仓者建议</span></template>
        <p class="text-sm leading-relaxed">{{ dashboard.advice?.holder || '暂无建议' }}</p>
      </el-card>
      <el-card>
        <template #header><span class="font-semibold">🔵 空仓者建议</span></template>
        <p class="text-sm leading-relaxed">{{ dashboard.advice?.empty || '暂无建议' }}</p>
      </el-card>
    </div>

    <!-- 技术面数据 -->
    <el-card class="mt-4">
      <template #header><span class="font-semibold">📐 技术面分析</span></template>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="tech-item">
          <div class="tech-label">趋势</div>
          <div class="tech-value" :class="trendColor">{{ dashboard.technical?.trend }}</div>
          <div class="tech-sub">评分: {{ dashboard.technical?.trend_score }}/100</div>
        </div>
        <div class="tech-item">
          <div class="tech-label">MA5 / MA10 / MA20</div>
          <div class="tech-value text-sm">
            {{ dashboard.technical?.ma5?.toFixed(2) }} /
            {{ dashboard.technical?.ma10?.toFixed(2) }} /
            {{ dashboard.technical?.ma20?.toFixed(2) }}
          </div>
        </div>
        <div class="tech-item">
          <div class="tech-label">乖离率</div>
          <div class="tech-value">{{ dashboard.technical?.bias5?.toFixed(2) }}%</div>
          <div class="tech-sub" :class="biasRiskColor">{{ dashboard.technical?.bias_risk }}</div>
        </div>
        <div class="tech-item">
          <div class="tech-label">量能</div>
          <div class="tech-value text-sm">{{ dashboard.technical?.volume_status }}</div>
          <div class="tech-sub">量比: {{ dashboard.technical?.volume_ratio?.toFixed(2) }}</div>
        </div>
        <div class="tech-item">
          <div class="tech-label">MACD</div>
          <div class="tech-value text-sm">{{ dashboard.technical?.macd_status }}</div>
        </div>
        <div class="tech-item">
          <div class="tech-label">RSI(6)</div>
          <div class="tech-value">{{ dashboard.technical?.rsi_6?.toFixed(1) }}</div>
          <div class="tech-sub">{{ dashboard.technical?.rsi_status }}</div>
        </div>
        <div class="tech-item">
          <div class="tech-label">支撑位</div>
          <div class="tech-value text-green-600">{{ dashboard.technical?.support?.toFixed(2) }}</div>
        </div>
        <div class="tech-item">
          <div class="tech-label">压力位</div>
          <div class="tech-value text-red-600">{{ dashboard.technical?.resistance?.toFixed(2) }}</div>
        </div>
      </div>
    </el-card>

    <!-- 交易狙击方案 -->
    <el-card class="mt-4">
      <template #header><span class="font-semibold">🎯 交易狙击方案</span></template>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div class="trade-point buy">
          <div class="trade-label">理想买入区间</div>
          <div class="trade-value">{{ dashboard.trade_plan?.buy_zone_1 }}</div>
        </div>
        <div class="trade-point buy">
          <div class="trade-label">二次加仓区间</div>
          <div class="trade-value">{{ dashboard.trade_plan?.buy_zone_2 }}</div>
        </div>
        <div class="trade-point stop">
          <div class="trade-label">硬性止损</div>
          <div class="trade-value">{{ dashboard.trade_plan?.stop_loss }}</div>
        </div>
        <div class="trade-point target">
          <div class="trade-label">第一目标</div>
          <div class="trade-value">{{ dashboard.trade_plan?.target_1 }}</div>
        </div>
        <div class="trade-point target">
          <div class="trade-label">第二目标</div>
          <div class="trade-value">{{ dashboard.trade_plan?.target_2 }}</div>
        </div>
      </div>
    </el-card>

    <!-- 操作检查清单 -->
    <el-card class="mt-4">
      <template #header><span class="font-semibold">✅ 操作检查清单</span></template>
      <div class="space-y-2">
        <div v-for="item in dashboard.checklist" :key="item.item"
          class="flex items-center gap-3 p-2 rounded"
          :class="item.status === '✅' ? 'bg-green-50' : item.status === '❌' ? 'bg-red-50' : 'bg-yellow-50'">
          <span class="text-xl">{{ item.status }}</span>
          <span class="font-medium">{{ item.item }}</span>
          <span class="text-sm text-gray-500 ml-auto">{{ item.detail }}</span>
        </div>
      </div>
    </el-card>

    <!-- 关联资讯 -->
    <el-card class="mt-4" v-if="dashboard.related_news?.length">
      <template #header><span class="font-semibold">📰 关联资讯</span></template>
      <div v-for="news in dashboard.related_news" :key="news.news_id" class="py-2 border-b last:border-0">
        <div class="flex items-start justify-between">
          <span class="text-sm font-medium">{{ news.title }}</span>
          <el-tag v-if="news.sentiment" size="small" :type="getSentimentType(news.sentiment)">
            {{ news.sentiment }}
          </el-tag>
        </div>
        <div class="text-xs text-gray-400 mt-1">{{ news.source }} · {{ news.publish_time }}</div>
      </div>
    </el-card>

    <!-- 关联研报 -->
    <el-card class="mt-4" v-if="dashboard.related_reports?.length">
      <template #header><span class="font-semibold">📄 关联研报</span></template>
      <div v-for="r in dashboard.related_reports" :key="r.report_id" class="py-2 border-b last:border-0">
        <div class="text-sm font-medium">{{ r.title }}</div>
        <div class="text-xs text-gray-400 mt-1">{{ r.source }} · {{ r.publish_time }}</div>
      </div>
    </el-card>

    <!-- AI 深度解读 -->
    <el-card class="mt-4" v-if="dashboard.markdown">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">🤖 AI 完整分析报告</span>
          <el-button size="small" @click="copyMarkdown">复制</el-button>
        </div>
      </template>
      <div class="markdown-body" v-html="renderMarkdown(dashboard.markdown)"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../composables/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(false)
const dashboard = ref({})

const priceColor = computed(() => {
  const pct = dashboard.value.quote?.change_pct || 0
  return pct > 0 ? 'text-red-600' : pct < 0 ? 'text-green-600' : 'text-gray-600'
})

const sentimentClass = computed(() => {
  const s = dashboard.value.sentiment
  if (s === '看多') return 'bg-red-100 text-red-700'
  if (s === '看空') return 'bg-green-100 text-green-700'
  return 'bg-gray-100 text-gray-700'
})

const trendColor = computed(() => {
  const t = dashboard.value.technical?.trend || ''
  if (t.includes('多头') || t.includes('强势')) return 'text-red-600'
  if (t.includes('空头')) return 'text-green-600'
  return 'text-gray-600'
})

const biasRiskColor = computed(() => {
  const r = dashboard.value.technical?.bias_risk
  if (r === '安全') return 'text-green-600'
  if (r === '警戒') return 'text-yellow-600'
  return 'text-red-600'
})

onMounted(() => fetchDashboard())

async function fetchDashboard() {
  loading.value = true
  try {
    const code = route.params.code || route.query.code
    const name = route.query.name || ''
    const res = await api.get(`/api/dashboard/stock/${code}`, { params: { stock_name: name } })
    dashboard.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function getSentimentType(s) {
  if (s === '利好') return 'success'
  if (s === '利空') return 'danger'
  return 'info'
}

function renderMarkdown(md) {
  // Simple markdown rendering
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
  navigator.clipboard.writeText(dashboard.value.markdown)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 12px;
}
.header-card .text-gray-400 { color: rgba(255,255,255,0.7); }
.header-card .text-gray-500 { color: rgba(255,255,255,0.8); }
.tech-item {
  text-align: center;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}
.tech-label { font-size: 12px; color: #9ca3af; margin-bottom: 4px; }
.tech-value { font-size: 18px; font-weight: bold; }
.tech-sub { font-size: 12px; color: #6b7280; margin-top: 2px; }
.trade-point {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
}
.trade-point.buy { background: #fef2f2; border: 1px solid #fecaca; }
.trade-point.stop { background: #fef3c7; border: 1px solid #fde68a; }
.trade-point.target { background: #f0fdf4; border: 1px solid #bbf7d0; }
.trade-label { font-size: 12px; color: #6b7280; margin-bottom: 4px; }
.trade-value { font-size: 16px; font-weight: bold; }
.markdown-body { font-size: 14px; line-height: 1.8; }
.markdown-body h1 { font-size: 20px; font-weight: bold; margin: 16px 0 8px; }
.markdown-body h2 { font-size: 18px; font-weight: bold; margin: 14px 0 6px; }
.markdown-body h3 { font-size: 16px; font-weight: bold; margin: 12px 0 4px; }
.markdown-body strong { color: #1f2937; }
.markdown-body li { margin-left: 16px; list-style: disc; }
</style>
