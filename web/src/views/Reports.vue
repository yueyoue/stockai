<template>
  <div class="page-container">
    <h2 class="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">📄 研报中心</h2>

    <!-- Filters -->
    <el-card class="mb-4">
      <div class="flex flex-wrap gap-3">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索研报标题、股票代码"
          clearable
          class="flex-1 min-w-[150px]"
          @keyup.enter="fetchReports"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filters.report_type" placeholder="分类" clearable class="w-28">
          <el-option label="个股研报" value="个股研报" />
          <el-option label="行业研报" value="行业研报" />
          <el-option label="大盘宏观" value="大盘宏观研报" />
        </el-select>
        <el-button type="primary" @click="fetchReports" :icon="Search">搜索</el-button>
      </div>
    </el-card>

    <!-- Report list -->
    <el-card>
      <div v-if="loading" class="text-center py-12">
        <el-icon class="is-loading text-2xl"><Loading /></el-icon>
      </div>
      <div v-else-if="reports.length === 0" class="text-center py-12 text-gray-400">暂无研报数据</div>

      <!-- Desktop table -->
      <div class="hidden md:block">
        <el-table :data="reports" stripe @row-click="showDetail">
          <el-table-column prop="title" label="标题" min-width="250" show-overflow-tooltip />
          <el-table-column prop="source" label="来源" width="100" />
          <el-table-column prop="report_type" label="分类" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="getTagType(row.report_type)">{{ row.report_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="industry" label="行业" width="80" />
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
        <div v-for="report in reports" :key="report.report_id"
          class="p-3 border-b active:bg-gray-50" @click="showDetail(report)">
          <div class="font-medium text-sm line-clamp-2">{{ report.title }}</div>
          <div class="flex items-center gap-2 mt-2 flex-wrap">
            <el-tag size="small" :type="getTagType(report.report_type)">{{ report.report_type }}</el-tag>
            <span class="text-xs text-gray-400">{{ report.source }}</span>
            <span class="text-xs text-gray-400">{{ formatDate(report.publish_time) }}</span>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-4 flex justify-center">
        <el-pagination v-model:current-page="pagination.page" :page-size="pagination.pageSize"
          :total="pagination.total" layout="prev, pager, next" @current-change="fetchReports" small />
      </div>
    </el-card>

    <!-- Detail dialog -->
    <el-dialog v-model="detailVisible" :title="selectedReport?.title" width="700px" top="5vh"
      :fullscreen="isMobile" class="detail-dialog">
      <div v-if="selectedReport" class="detail-content">
        <div class="mb-4 flex flex-wrap items-center gap-2">
          <el-tag :type="getTagType(selectedReport.report_type)">{{ selectedReport.report_type }}</el-tag>
          <span class="text-sm text-gray-500">{{ selectedReport.source }}</span>
          <span class="text-sm text-gray-500">{{ formatDate(selectedReport.publish_time) }}</span>
        </div>
        
        <div v-if="selectedReport.related_stock" class="mb-3 text-sm">
          <span class="text-gray-500">关联股票：</span>{{ selectedReport.related_stock }}
        </div>
        <div v-if="selectedReport.industry" class="mb-3 text-sm">
          <span class="text-gray-500">所属行业：</span>{{ selectedReport.industry }}
        </div>

        <el-divider />

        <h4 class="font-semibold mb-3">🤖 AI 解读</h4>
        <div v-if="detailLoading" class="text-center py-4">
          <el-icon class="is-loading"><Loading /></el-icon> 加载中...
        </div>
        <div v-else-if="detailData?.ai_summary" class="ai-content">
          <div v-html="renderMarkdown(detailData.ai_summary)"></div>
        </div>
        <div v-else class="text-gray-400 text-sm py-4">暂无AI解读</div>

        <div v-if="selectedReport.url" class="mt-4">
          <a :href="selectedReport.url" target="_blank" class="text-blue-500 text-sm">
            查看原文 →
          </a>
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
const reports = ref([])
const filters = ref({ keyword: '', report_type: '' })
const pagination = ref({ page: 1, pageSize: 20, total: 0 })
const detailVisible = ref(false)
const selectedReport = ref(null)
const detailData = ref(null)
const detailLoading = ref(false)

onMounted(() => fetchReports())

async function fetchReports() {
  loading.value = true
  try {
    const res = await api.get('/api/reports', { params: { page: pagination.value.page, page_size: pagination.value.pageSize, ...filters.value } })
    reports.value = res.data.items
    pagination.value.total = res.data.total
  } catch {} finally { loading.value = false }
}

async function showDetail(report) {
  selectedReport.value = report
  detailData.value = null
  detailVisible.value = true
  detailLoading.value = true
  try {
    const res = await api.get(`/api/reports/${report.report_id}/detail`)
    detailData.value = res.data
  } catch {} finally { detailLoading.value = false }
}

function formatDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return `${dt.getMonth()+1}/${dt.getDate()} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
}

function getTagType(t) {
  if (t?.includes('个股')) return 'primary'
  if (t?.includes('行业')) return 'success'
  return 'warning'
}

function renderMarkdown(md) {
  if (!md) return ''
  return md
    .replace(/^### (.+)$/gm, '<h3 class="text-base font-bold mt-4 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-lg font-bold mt-4 mb-2">$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.ai-content {
  background: #f9fafb;
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
