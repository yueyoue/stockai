<template>
  <div class="page-container">
    <h2 class="text-2xl font-bold mb-6">📄 研报中心</h2>

    <!-- Filters -->
    <el-card class="mb-6">
      <div class="flex flex-wrap gap-4">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索研报标题、股票代码、行业"
          clearable
          class="w-full sm:w-64"
          @keyup.enter="fetchReports"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="filters.report_type" placeholder="研报分类" clearable class="w-32">
          <el-option label="个股研报" value="个股研报" />
          <el-option label="行业研报" value="行业研报" />
          <el-option label="大盘宏观研报" value="大盘宏观研报" />
        </el-select>

        <el-button type="primary" @click="fetchReports">搜索</el-button>
      </div>
    </el-card>

    <!-- Report list -->
    <el-card>
      <div v-if="loading" class="text-center py-12">
        <el-icon class="is-loading text-2xl"><Loading /></el-icon>
        <p class="text-gray-400 mt-2">加载中...</p>
      </div>
      
      <div v-else-if="reports.length === 0" class="text-center py-12 text-gray-400">
        暂无研报数据
      </div>

      <!-- Desktop table -->
      <div class="hidden md:block">
        <el-table :data="reports" stripe>
          <el-table-column prop="title" label="标题" min-width="300">
            <template #default="{ row }">
              <div class="cursor-pointer hover:text-blue-600" @click="showDetail(row)">
                {{ row.title }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="120" />
          <el-table-column prop="report_type" label="分类" width="120">
            <template #default="{ row }">
              <el-tag size="small" :type="getTagType(row.report_type)">{{ row.report_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="industry" label="行业" width="100" />
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
          v-for="report in reports"
          :key="report.report_id"
          class="p-4 border-b hover:bg-gray-50"
          @click="showDetail(report)"
        >
          <div class="font-medium text-sm">{{ report.title }}</div>
          <div class="flex items-center gap-2 mt-2">
            <el-tag size="small" :type="getTagType(report.report_type)">{{ report.report_type }}</el-tag>
            <span class="text-xs text-gray-400">{{ report.source }}</span>
            <span class="text-xs text-gray-400">{{ formatDateTime(report.publish_time) }}</span>
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
          @current-change="fetchReports"
        />
      </div>
    </el-card>

    <!-- Detail dialog -->
    <el-dialog v-model="detailVisible" :title="selectedReport?.title" width="700px" top="5vh">
      <div v-if="selectedReport">
        <div class="mb-4">
          <el-tag :type="getTagType(selectedReport.report_type)">{{ selectedReport.report_type }}</el-tag>
          <span class="ml-2 text-sm text-gray-500">{{ selectedReport.source }}</span>
          <span class="ml-2 text-sm text-gray-500">{{ formatDateTime(selectedReport.publish_time) }}</span>
        </div>
        
        <div v-if="selectedReport.related_stock" class="mb-4 text-sm">
          <span class="text-gray-500">关联股票：</span>{{ selectedReport.related_stock }}
        </div>
        
        <div v-if="selectedReport.industry" class="mb-4 text-sm">
          <span class="text-gray-500">所属行业：</span>{{ selectedReport.industry }}
        </div>

        <el-divider />
        
        <h4 class="font-semibold mb-2">AI 解读</h4>
        <div v-if="selectedReport.ai_summary" class="bg-gray-50 p-4 rounded-lg text-sm whitespace-pre-wrap">
          {{ selectedReport.ai_summary }}
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
const reports = ref([])
const filters = ref({ keyword: '', report_type: '' })
const pagination = ref({ page: 1, pageSize: 20, total: 0 })
const detailVisible = ref(false)
const selectedReport = ref(null)

onMounted(() => fetchReports())

async function fetchReports() {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      ...filters.value,
    }
    const res = await api.get('/api/reports', { params })
    reports.value = res.data.items
    pagination.value.total = res.data.total
  } catch {} finally {
    loading.value = false
  }
}

function showDetail(report) {
  selectedReport.value = report
  detailVisible.value = true
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function getTagType(type) {
  if (type?.includes('个股')) return 'primary'
  if (type?.includes('行业')) return 'success'
  return 'warning'
}
</script>
