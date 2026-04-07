<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const password = ref('')
const error = ref('')
const loading = ref(false)
const API = import.meta.env.VITE_API_URL || ''

const login = async () => {
  if (!password.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API}/api/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: password.value })
    })
    if (res.ok) {
      const data = await res.json()
      localStorage.setItem('admin_auth', 'true')
      localStorage.setItem('admin_token', data.token)
      router.push('/admin')
    } else {
      error.value = '密码错误，请重试'
      password.value = ''
    }
  } catch {
    error.value = '无法连接到服务器，请检查后端是否启动'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">⚙</div>
      <h1 class="login-title">SceneRank</h1>
      <p class="login-sub">管理员登录</p>
      <form @submit.prevent="login" class="login-form">
        <input
          v-model="password"
          type="password"
          placeholder="请输入管理员密码"
          class="login-input"
          autofocus
        />
        <p class="error-msg" v-if="error">{{ error }}</p>
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <a href="#/survey" class="back-link">← 返回问卷</a>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4f46e5 100%);
  display: flex; align-items: center; justify-content: center; padding: 1rem;
}
.login-card {
  background: white; border-radius: 24px; padding: 2.5rem 2rem;
  width: 100%; max-width: 380px; text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.login-logo {
  width: 56px; height: 56px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border-radius: 16px; display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; margin: 0 auto 1rem;
}
.login-title { font-size: 1.6rem; font-weight: 800; color: #1e1b4b; margin: 0 0 0.3rem; }
.login-sub { color: #9ca3af; font-size: 0.9rem; margin: 0 0 2rem; }
.login-form { display: flex; flex-direction: column; gap: 0.8rem; }
.login-input {
  padding: 0.85rem 1rem; border: 1.5px solid #e5e7eb; border-radius: 12px;
  font-size: 1rem; text-align: center; transition: border-color 0.2s, box-shadow 0.2s;
}
.login-input:focus { border-color: #4f46e5; outline: none; box-shadow: 0 0 0 3px rgba(79,70,229,0.12); }
.error-msg { color: #ef4444; font-size: 0.85rem; margin: 0; }
.login-btn {
  padding: 0.9rem; background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white; border: none; border-radius: 12px; font-size: 1rem; font-weight: 700;
  cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 14px rgba(79,70,229,0.35);
}
.login-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.back-link { display: block; margin-top: 1.5rem; color: #9ca3af; font-size: 0.85rem; text-decoration: none; }
.back-link:hover { color: #4f46e5; }
</style>
