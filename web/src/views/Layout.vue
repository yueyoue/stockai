<template>
  <div class="app-layout">
    <!-- Mobile header -->
    <div class="mobile-header">
      <h1 class="text-lg font-bold text-blue-600">📈 StockAI</h1>
      <el-button :icon="Menu" @click="drawerVisible = true" circle size="small" />
    </div>

    <div class="app-body">
      <!-- Sidebar for desktop ONLY -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h1 class="text-2xl font-bold text-blue-600">📈 StockAI</h1>
          <p class="text-xs text-gray-400 mt-1">智能研报分析平台</p>
        </div>
        <el-menu
          :default-active="currentRoute"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/">
            <el-icon><DataBoard /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item index="/reports">
            <el-icon><Document /></el-icon>
            <span>研报中心</span>
          </el-menu-item>
          <el-menu-item index="/news">
            <el-icon><Collection /></el-icon>
            <span>市场资讯</span>
          </el-menu-item>
          <el-menu-item index="/watchlist">
            <el-icon><Star /></el-icon>
            <span>我的自选</span>
          </el-menu-item>
          <el-menu-item index="/push">
            <el-icon><Bell /></el-icon>
            <span>推送设置</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin">
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <!-- Mobile drawer -->
      <el-drawer v-model="drawerVisible" direction="ltr" size="260px" :with-header="false">
        <div class="p-4 border-b">
          <h1 class="text-xl font-bold text-blue-600">📈 StockAI</h1>
          <p class="text-xs text-gray-400 mt-1">智能研报分析平台</p>
        </div>
        <el-menu :default-active="currentRoute" router @select="drawerVisible = false">
          <el-menu-item index="/">
            <el-icon><DataBoard /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item index="/reports">
            <el-icon><Document /></el-icon>
            <span>研报中心</span>
          </el-menu-item>
          <el-menu-item index="/news">
            <el-icon><Collection /></el-icon>
            <span>市场资讯</span>
          </el-menu-item>
          <el-menu-item index="/watchlist">
            <el-icon><Star /></el-icon>
            <span>我的自选</span>
          </el-menu-item>
          <el-menu-item index="/push">
            <el-icon><Bell /></el-icon>
            <span>推送设置</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin">
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </el-menu-item>
        </el-menu>
      </el-drawer>

      <!-- Main content area -->
      <div class="main-area">
        <!-- Top bar (desktop) -->
        <header class="top-bar">
          <div></div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-gray-600">{{ authStore.user?.username }}</span>
            <el-tag v-if="authStore.isAdmin" type="danger" size="small">管理员</el-tag>
            <el-button text size="small" @click="handleLogout">退出</el-button>
          </div>
        </header>

        <!-- Content -->
        <main class="main-content">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { DataBoard, Document, Collection, Star, Bell, Setting, Menu } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const drawerVisible = ref(false)
const currentRoute = computed(() => route.path)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* === 基础布局 === */
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh; /* 移动端安全高度 */
  overflow: hidden;
  background: #f5f7fa;
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* === 移动端头部 === */
.mobile-header {
  display: none;
}

/* === 桌面端侧边栏 === */
.sidebar {
  width: 220px;
  min-width: 220px;
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 24px 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

/* === 主内容区 === */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.top-bar {
  height: 56px;
  min-height: 56px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: 16px;
}

/* === 移动端适配 === */
@media (max-width: 768px) {
  /* 显示移动端头部 */
  .mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 50px;
    min-height: 50px;
    padding: 0 16px;
    background: #fff;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    flex-shrink: 0;
    z-index: 10;
  }

  /* 隐藏桌面侧边栏 */
  .sidebar {
    display: none !important;
  }

  /* 隐藏桌面顶栏 */
  .top-bar {
    display: none !important;
  }

  /* 主内容区适配 */
  .main-content {
    padding: 12px;
  }
}

/* === 平板适配 === */
@media (min-width: 769px) and (max-width: 1024px) {
  .sidebar {
    width: 180px;
    min-width: 180px;
  }

  .main-content {
    padding: 16px;
  }
}
</style>
