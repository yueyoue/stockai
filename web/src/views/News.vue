<template>
  <div class="page-container">
    <h2 class="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">📰 市场资讯</h2>

    <!-- Filters -->
    <el-card class="mb-4">
      <div class="flex flex-wrap gap-3">
        <el-input v-model="filters.keyword" placeholder="搜索资讯标题" clearable
          class="flex-1 min-w-[150px]" @keyup.enter="fetchNews">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filters.news_type" placeholder="分类" clearable class="w-24">
          <el-option label="个股" value="个股资讯" />
          <el-option label="行业" value="行业资讯" />
          <el-option label="大盘" value="大盘宏观" />
          <el-option label="公告" value="公告" />
        </el-select>
        <el-select v-model="filters.sentiment" placeholder="情绪" clearable class="w-20">
          <el-option label="利好" value="利好" />
          <el-option label="中性" value="中性" />
          <el-option label="利空" value="利空" />
        </el-select>
        <el-button type="primary" @click="fetchNews" :icon="Search">搜索</el-button>
      </div>
    </el-card>

    <!-- News list -->
    <el-card>
      <div v-if="loading" class="text-center py-12">
        <el-icon class="is-loading text-2xl"><Loading /></el-icon>
      </div>
      <div v-else-if="newsList.length === 0" class="text-center py-12 text-gray-400">暂无资讯数据</div>

      <!-- Desktop table -->
      <div class="hidden md:block">
        <el-table :data="newsList" stripe @row-click="showDetail">
          <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip />
          <el-table-column prop="news_type" label="分类" width="80">
            <template #default="{ row }"><el-tag size="small">{{ row.news_type }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="sentiment" label="情绪" width="70">
            <template #default="{ row }">
              <el-tag v-if="row.sentiment" size="small" :type="getSentimentType(row.sentiment)">{{ row.sentiment }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="80" />
          <el-table-column prop="publish_time" label="时间" width="140">
            <template #default="{ row }">{{ formatDate(row.publish_time) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button text type="primary" size="small" @click.stop="showDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Mobile cards -->
      <div class="md:hidden">
        <div v-for="news in newsList" :key="news.news_id"
          class="p-3 border-b active:bg-gray-50" @click="showDetail(news)">
          <div class="font-medium text-sm line-clamp-2">{{ news.title }}</div>
          <div class="flex items-center gap-2 mt-2 flex-wrap">
            <el-tag size="small">{{ news.news_type }}</el-tag>
            <el-tag v-if="news.sentiment" size="small" :type="getSentimentType(news.sentiment)">{{ news.sentiment }}</el-tag>
            <span class="text-xs text-gray-400">{{ formatDate(news.publish_time) }}</span>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-4 flex justify-center">
        <el-pagination v-model:current-page="pagination.page" :page-size="pagination.pageSize"
          :total="pagination.total" layout="prev, pager, next" @current-change="fetchNews" small />
      </div>
    </el-card>

    <!-- Detail dialog -->
    <el-dialog v-model="detailVisible" :title="selectedNews?.title" width="700px" top="5vh"
      :fullscreen="isMobile" class="detail-dialog">
      <div v-if="selectedNews" class="detail-content">
        <div class="mb-4 flex flex-wrap items-center gap-2">
          <el-tag size="small">{{ selectedNews.news_type }}</el-tag>
          <el-tag v-if="selectedNews.sentiment" size="small" :type="getSentimentType(selectedNews.sentiment)">
            {{ selectedNews.sentiment }}
          </el-tag>
          <span class="text-sm text-gray-500">{{ selectedNews.source }}</span>
          <span class="text-sm text-gray-500">{{ formatDate(selectedNews.publish_time) }}</span>
        </div>

        <!-- 正文内容 -->
        <div v-if="detailLoading" class="text-center py-4">
          <el-icon class="is-loading"><Loading /></el-icon> 加载中...
        </div>
        <template v-else>
          <div v-if="detailData?.content" class="article-content">
            {{ detailData.content }}
          </div>
          <div v-else class="text-gray-400 text-sm py-4">暂无正文内容</div>
        </template>

        <el-divider />

        <!-- AI 解读 -->
        <h4 class="font-semibold mb-3">🤖 AI 影响解读</h4>
        <div v-if="detailData?.ai_impact" class="ai-content">
          <div v-html="renderMarkdown(detailData.ai_impact)"></div>
        </div>
        <div v-else class="text-gray-400 text-sm">暂无AI解读</div>

        <div v-if="selectedNews?.url" class="mt-4">
          <a :href="selectedNews.url" target="_blank" class="text-blue-500 text-sm">查看原文 →</a>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Loading } from '@element-plus/icons-vue'
import api from '../composables/api'

const isMobile = computed(() => window.innerWidth < 768)
const loading = ref(false)
const newsList = ref([])
const filters = ref({ keyword: '', news_type: '', sentiment: '' })
const pagination = ref({ page: 1, pageSize: 20, total: 0 })
const detailVisible = ref(false)
const selectedNews = ref(null)
const detailData = ref(null)
const detailLoading = ref(false)

onMounted(() => fetchNews())

async function fetchNews() {
  loading.value = true
  try {
    const res = await api.get('/api/news', { params: { page: pagination.value.page, page_size: pagination.value.pageSize, ...filters.value } })
    newsList.value = res.data.items
    pagination.value.total = res.data.total
  } catch {} finally { loading.value = false }
}

async function showDetail(news) {
  selectedNews.value = news
  detailData.value = null
  detailVisible.value = true
  detailLoading.value = true
  try {
    const res = await api.get(`/api/news/${news.news_id}/detail`)
    detailData.value = res.data
  } catch {} finally { detailLoading.value = false }
}

function formatDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return `${dt.getMonth()+1}/${dt.getDate()} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
}

function getSentimentType(s) {
  if (s === '利好') return 'success'
  if (s === '利空') return 'danger'
  return 'info'
}

function renderMarkdown(md) {
  if (!md) return ''
  return md
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.article-content {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  font-size: 14px;
  line-height: 1.8;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
}
.ai-content {
  background: #fffbeb;
  border-radius: 8px;
  padding: 16px;
  font-size: 14px;
  line-height: 1.8;
}
@media (max-width: 768px) {
  .detail-dialog :deep(.el-dialog) {
    margin: 0 !important;
    border-radius: 12px 12px 0 0;
    max-height: 85vh;
    overflow-y: auto;
  }
}
</style>
