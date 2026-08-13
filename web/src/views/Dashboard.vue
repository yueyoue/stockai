<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">📊 数据看板</h2>

    <!-- Stats cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <el-card class="hover-card" shadow="hover">
        <div class="text-center">
          <div class="text-3xl font-bold text-blue-600">{{ stats.reports }}</div>
          <div class="text-sm text-gray-500 mt-1">研报总数</div>
        </div>
      </el-card>
      <el-card class="hover-card" shadow="hover">
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600">{{ stats.news }}</div>
          <div class="text-sm text-gray-500 mt-1">资讯总数</div>
        </div>
      </el-card>
      <el-card class="hover-card" shadow="hover">
        <div class="text-center">
          <div class="text-3xl font-bold text-orange-600">{{ watchlistCount }}</div>
          <div class="text-sm text-gray-500 mt-1">自选股票</div>
        </div>
      </el-card>
      <el-card class="hover-card" shadow="hover">
        <div class="text-center">
          <div class="text-3xl font-bold text-purple-600">{{ stats.users }}</div>
          <div class="text-sm text-gray-500 mt-1">注册用户</div>
        </div>
      </el-card>
    </div>

    <!-- Recent reports -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="mb-6">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-semibold">📄 最新研报</span>
              <el-button text type="primary" @click="$router.push('/reports')">查看更多</el-button>
            </div>
          </template>
          <div v-if="recentReports.length === 0" class="text-center text-gray-400 py-8">
            暂无研报数据
          </div>
          <div v-else>
            <div
              v-for="report in recentReports"
              :key="report.report_id"
              class="py-3 border-b last:border-0 hover:bg-gray-50 cursor-pointer"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="font-medium text-sm line-clamp-2">{{ report.title }}</div>
                  <div class="text-xs text-gray-400 mt-1">
                    {{ report.source }} · {{ formatDate(report.publish_time) }}
                  </div>
                </div>
                <el-tag size="small" :type="getReportTagType(report.report_type)">
                  {{ report.report_type }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="mb-6">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-semibold">📰 最新资讯</span>
              <el-button text type="primary" @click="$router.push('/news')">查看更多</el-button>
            </div>
          </template>
          <div v-if="recentNews.length === 0" class="text-center text-gray-400 py-8">
            暂无资讯数据
          </div>
          <div v-else>
            <div
              v-for="news in recentNews"
              :key="news.news_id"
              class="py-3 border-b last:border-0 hover:bg-gray-50 cursor-pointer"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="font-medium text-sm line-clamp-2">{{ news.title }}</div>
                  <div class="text-xs text-gray-400 mt-1">
                    {{ news.source }} · {{ formatDate(news.publish_time) }}
                  </div>
                </div>
                <el-tag
                  v-if="news.sentiment"
                  size="small"
                  :type="getSentimentType(news.sentiment)"
                >
                  {{ news.sentiment }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../composables/api'

const stats = ref({ reports: 0, news: 0, users: 0 })
const watchlistCount = ref(0)
const recentReports = ref([])
const recentNews = ref([])

onMounted(async () => {
  await Promise.all([
    fetchStats(),
    fetchWatchlist(),
    fetchRecentReports(),
    fetchRecentNews(),
  ])
})

async function fetchStats() {
  try {
    const res = await api.get('/api/stats')
    stats.value = res.data
  } catch {}
}

async function fetchWatchlist() {
  try {
    const res = await api.get('/api/watchlist')
    watchlistCount.value = res.data.length
  } catch {}
}

async function fetchRecentReports() {
  try {
    const res = await api.get('/api/reports?page_size=5')
    recentReports.value = res.data.items
  } catch {}
}

async function fetchRecentNews() {
  try {
    const res = await api.get('/api/news?page_size=5')
    recentNews.value = res.data.items
  } catch {}
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

function getReportTagType(type) {
  if (type?.includes('个股')) return 'primary'
  if (type?.includes('行业')) return 'success'
  return 'warning'
}

function getSentimentType(sentiment) {
  if (sentiment === '利好') return 'success'
  if (sentiment === '利空') return 'danger'
  return 'info'
}
</script>
