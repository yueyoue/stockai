<template>
  <div class="app-layout">
    <!-- Mobile header -->
    <div class="lg:hidden flex items-center justify-between bg-white shadow-sm px-4 h-14">
      <h1 class="text-xl font-bold text-blue-600">📈 StockAI</h1>
      <el-button :icon="Menu" @click="drawerVisible = true" />
    </div>

    <div class="app-body">
      <!-- Sidebar for desktop -->
      <aside class="sidebar hidden lg:block">
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
      <el-drawer v-model="drawerVisible" direction="ltr" size="250px">
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
        <!-- Top bar -->
        <header class="top-bar hidden lg:flex">
          <div></div>
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600">{{ authStore.user?.username }}</span>
            <el-tag v-if="authStore.isAdmin" type="danger" size="small">管理员</el-tag>
            <el-button text @click="handleLogout">退出</el-button>
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
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  min-width: 220px;
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  padding: 24px 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

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
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: #f5f7fa;
  padding: 20px;
}
</style>
