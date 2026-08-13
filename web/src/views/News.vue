<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">📰 市场资讯</h2>

    <!-- Filters -->
    <el-card class="mb-6">
      <div class="flex flex-wrap gap-4">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索资讯标题、股票代码"
          clearable
          class="w-full sm:w-64"
          @keyup.enter="fetchNews"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="filters.news_type" placeholder="资讯分类" clearable class="w-32">
          <el-option label="个股资讯" value="个股资讯" />
          <el-option label="行业资讯" value="行业资讯" />
          <el-option label="大盘宏观" value="大盘宏观" />
          <el-option label="公告" value="公告" />
        </el-select>

        <el-select v-model="filters.sentiment" placeholder="情绪筛选" clearable class="w-28">
          <el-option label="利好" value="利好" />
          <el-option label="中性" value="中性" />
          <el-option label="利空" value="利空" />
        </el-select>

        <el-button type="primary" @click="fetchNews">搜索</el-button>
      </div>
    </el-card>

    <!-- News list -->
    <el-card>
      <div v-if="loading" class="text-center py-12">
        <el-icon class="is-loading text-2xl"><Loading /></el-icon>
      </div>
      
      <div v-else-if="newsList.length === 0" class="text-center py-12 text-gray-400">
        暂无资讯数据
      </div>

      <!-- Desktop table -->
      <div class="hidden md:block">
        <el-table :data="newsList" stripe>
          <el-table-column prop="title" label="标题" min-width="300">
            <template #default="{ row }">
              <div class="cursor-pointer hover:text-blue-600" @click="showDetail(row)">
                {{ row.title }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="news_type" label="分类" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ row.news_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="sentiment" label="情绪" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.sentiment" size="small" :type="getSentimentType(row.sentiment)">
                {{ row.sentiment }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="100" />
          <el-table-column prop="publish_time" label="时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.publish_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button text type="primary" size="small" @click="showDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Mobile cards -->
      <div class="md:hidden">
        <div
          v-for="news in newsList"
          :key="news.news_id"
          class="p-4 border-b hover:bg-gray-50"
          @click="showDetail(news)"
        >
          <div class="font-medium text-sm">{{ news.title }}</div>
          <div class="flex items-center gap-2 mt-2">
            <el-tag size="small">{{ news.news_type }}</el-tag>
            <el-tag v-if="news.sentiment" size="small" :type="getSentimentType(news.sentiment)">
              {{ news.sentiment }}
            </el-tag>
            <span class="text-xs text-gray-400">{{ formatDateTime(news.publish_time) }}</span>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-4 flex justify-center">
        <el-pagination
          v-model:current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          layout="prev, pager, next"
          @current-change="fetchNews"
        />
      </div>
    </el-card>

    <!-- Detail dialog -->
    <el-dialog v-model="detailVisible" :title="selectedNews?.title" width="700px" top="5vh">
      <div v-if="selectedNews">
        <div class="mb-4 flex items-center gap-2">
          <el-tag size="small">{{ selectedNews.news_type }}</el-tag>
          <el-tag v-if="selectedNews.sentiment" size="small" :type="getSentimentType(selectedNews.sentiment)">
            {{ selectedNews.sentiment }}
          </el-tag>
          <span class="text-sm text-gray-500">{{ selectedNews.source }}</span>
          <span class="text-sm text-gray-500">{{ formatDateTime(selectedNews.publish_time) }}</span>
        </div>

        <div v-if="selectedNews.content" class="mb-4 text-sm leading-relaxed">
          {{ selectedNews.content }}
        </div>

        <el-divider />

        <h4 class="font-semibold mb-2">AI 影响解读</h4>
        <div v-if="selectedNews.ai_impact" class="bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">
          {{ selectedNews.ai_impact }}
        </div>
        <div v-else class="text-gray-400 text-sm">暂无AI解读</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Loading } from '@element-plus/icons-vue'
import api from '../composables/api'

const loading = ref(false)
const newsList = ref([])
const filters = ref({ keyword: '', news_type: '', sentiment: '' })
const pagination = ref({ page: 1, pageSize: 20, total: 0 })
const detailVisible = ref(false)
const selectedNews = ref(null)

onMounted(() => fetchNews())

async function fetchNews() {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      ...filters.value,
    }
    const res = await api.get('/api/news', { params })
    newsList.value = res.data.items
    pagination.value.total = res.data.total
  } catch {} finally {
    loading.value = false
  }
}

function showDetail(news) {
  selectedNews.value = news
  detailVisible.value = true
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function getSentimentType(sentiment) {
  if (sentiment === '利好') return 'success'
  if (sentiment === '利空') return 'danger'
  return 'info'
}
</script>
