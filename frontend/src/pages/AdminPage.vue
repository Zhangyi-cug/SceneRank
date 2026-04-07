<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSurveyConfig, useSurveyResults } from '../composables/useSurvey.js'

const router = useRouter()
const { loadConfig, saveConfig, resetConfig } = useSurveyConfig()
const { loadResults, clearResults, deleteResult, exportCSV } = useSurveyResults()

const activeTab = ref('overview')
const config = ref(null)
const results = ref([])
const saveMsg = ref('')
const loading = ref(true)

onMounted(async () => {
  config.value = await loadConfig()
  results.value = await loadResults()
  loading.value = false
})

const save = async () => {
  await saveConfig(config.value)
  saveMsg.value = '已保存 ✓'
  setTimeout(() => saveMsg.value = '', 2000)
}

const reset = async () => {
  if (!confirm('确定要重置为默认配置吗？')) return
  config.value = await resetConfig()
}

const logout = () => {
  localStorage.removeItem('admin_auth')
  localStorage.removeItem('admin_token')
  router.push('/admin/login')
}

const copyLink = async () => {
  const url = window.location.origin + window.location.pathname + '#/survey'
  try {
    await navigator.clipboard.writeText(url)
    alert('问卷链接已复制：\n' + url)
  } catch {
    window.prompt('请手动复制链接：', url)
  }
}

const handleClear = async () => {
  if (!confirm('确定要清空所有收集的数据吗？此操作不可撤销。')) return
  await clearResults()
  results.value = []
}

const refreshData = async () => {
  results.value = await loadResults()
}

const handleDelete = async (id) => {
  if (!confirm('确定删除这条记录？')) return
  await deleteResult(id)
  results.value = results.value.filter(r => r.id !== id)
}

// 背景调查
const addQuestion = () => {
  config.value.background.questions.push({
    id: `q_${Date.now()}`, label: '新问题', type: 'select', required: true,
    options: [{ value: 'opt1', label: '选项1' }]
  })
}
const removeQuestion = (idx) => config.value.background.questions.splice(idx, 1)
const addOption = (q) => q.options.push({ value: `opt_${Date.now()}`, label: '新选项' })
const removeOption = (q, idx) => q.options.splice(idx, 1)

// 对比维度
const addDimension = () => {
  config.value.comparison.dimensions.push({
    id: `dim_${Date.now()}`, label: '新维度', question: '哪张图片更好？'
  })
}
const removeDimension = (idx) => config.value.comparison.dimensions.splice(idx, 1)

// 统计
const stats = computed(() => {
  const r = results.value
  return {
    total: r.length,
    participants: new Set(r.map(x => JSON.stringify(x.background))).size,
    today: r.filter(x => x.timestamp?.startsWith(new Date().toISOString().slice(0, 10))).length
  }
})

const tabs = [
  { id: 'overview',   icon: '📊', label: '概览' },
  { id: 'background', icon: '📝', label: '背景调查' },
  { id: 'comparison', icon: '🖼',  label: '图像对比' },
  { id: 'data',       icon: '📁', label: '数据管理' },
]

const statCards = computed(() => [
  { icon: '🗂',  val: stats.value.total,                          label: '已收集对比记录' },
  { icon: '👥', val: stats.value.participants,                    label: '参与人数（估算）' },
  { icon: '📅', val: stats.value.today,                           label: '今日新增' },
  { icon: '🎯', val: config.value?.comparison?.totalCount ?? '-', label: '每人目标次数' },
])
</script>

<template>
  <div class="admin">
    <header class="admin-header">
      <div class="header-inner">
        <div class="header-left">
          <div class="logo-mark">⚙</div>
          <div>
            <div class="logo-text">SceneRank 管理后台</div>
            <div class="survey-subtitle">{{ config?.title }}</div>
          </div>
        </div>
        <div class="header-right">
          <button class="hbtn" @click="copyLink">🔗 复制链接</button>
          <a href="#/survey" target="_blank" class="hbtn">👁 预览问卷</a>
          <button class="hbtn hbtn-danger" @click="logout">退出登录</button>
        </div>
      </div>
    </header>

    <nav class="tab-nav">
      <button v-for="t in tabs" :key="t.id"
        class="tab-btn" :class="{ active: activeTab === t.id }"
        @click="activeTab = t.id">
        <span>{{ t.icon }}</span>{{ t.label }}
      </button>
    </nav>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div class="admin-body" v-else-if="config">

      <!-- 概览 -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="stat-grid">
          <div class="stat-card" v-for="s in statCards" :key="s.label">
            <div class="stat-icon">{{ s.icon }}</div>
            <div class="stat-num">{{ s.val }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">问卷基本信息</div>
          <div class="form-row">
            <label>问卷标题</label>
            <input v-model="config.title" type="text" />
          </div>
          <div class="form-row">
            <label>问卷描述</label>
            <input v-model="config.description" type="text" />
          </div>
          <div class="form-row">
            <label>背景图 URL</label>
            <input v-model="config.coverImage" type="text" placeholder="输入图片链接，留空则无背景图" />
          </div>
          <div v-if="config.coverImage" class="cover-preview">
            <img :src="config.coverImage" alt="背景图预览" />
          </div>
        </div>

        <div class="save-bar">
          <button class="btn-primary" @click="save">保存配置</button>
          <span class="save-msg" v-if="saveMsg">{{ saveMsg }}</span>
          <button class="btn-ghost" @click="reset">重置默认</button>
        </div>
      </div>

      <!-- 背景调查 -->
      <div v-if="activeTab === 'background'" class="tab-content">
        <div class="panel-header-row">
          <div class="panel-title-lg">背景调查题目</div>
          <button class="btn-add" @click="addQuestion">＋ 添加题目</button>
        </div>

        <div v-if="!config.background.questions.length" class="empty-hint">
          暂无题目，点击右上角添加
        </div>

        <div v-for="(q, qi) in config.background.questions" :key="q.id" class="q-card">
          <div class="q-card-top">
            <span class="q-badge">Q{{ qi + 1 }}</span>
            <input v-model="q.label" class="q-input" placeholder="题目文字" />
            <select v-model="q.type" class="q-select">
              <option value="select">下拉选择</option>
              <option value="radio">单选按钮</option>
              <option value="text">文本输入</option>
            </select>
            <label class="q-check"><input type="checkbox" v-model="q.required" /> 必填</label>
            <button class="btn-del" @click="removeQuestion(qi)">✕</button>
          </div>
          <div v-if="q.type !== 'text'" class="opts-wrap">
            <div v-for="(opt, oi) in q.options" :key="oi" class="opt-row">
              <span class="opt-dot">·</span>
              <input v-model="opt.label" placeholder="选项文字" class="opt-input" />
              <input v-model="opt.value" placeholder="值" class="opt-val" />
              <button class="btn-del-sm" @click="removeOption(q, oi)">✕</button>
            </div>
            <button class="btn-add-opt" @click="addOption(q)">＋ 添加选项</button>
          </div>
        </div>

        <div class="save-bar">
          <button class="btn-primary" @click="save">保存配置</button>
          <span class="save-msg" v-if="saveMsg">{{ saveMsg }}</span>
        </div>
      </div>

      <!-- 图像对比 -->
      <div v-if="activeTab === 'comparison'" class="tab-content">
        <div class="panel">
          <div class="panel-title">基本设置</div>
          <div class="form-row">
            <label>说明文字</label>
            <input v-model="config.comparison.instruction" type="text" />
          </div>
          <div class="form-row">
            <label>每人对比次数</label>
            <input v-model.number="config.comparison.totalCount" type="number" min="1" class="input-sm" />
            <span class="input-hint">次</span>
          </div>
          <div class="form-row">
            <label>图片 ID 范围</label>
            <input v-model.number="config.comparison.imageRange.min" type="number" class="input-sm" placeholder="最小" />
            <span class="input-hint">—</span>
            <input v-model.number="config.comparison.imageRange.max" type="number" class="input-sm" placeholder="最大" />
          </div>
        </div>

        <div class="panel">
          <div class="panel-header-row">
            <div class="panel-title" style="margin-bottom:0">对比维度</div>
            <button class="btn-add" @click="addDimension">＋ 添加维度</button>
          </div>
          <div v-if="!config.comparison.dimensions.length" class="empty-hint">暂无维度</div>
          <div v-for="(dim, di) in config.comparison.dimensions" :key="dim.id" class="dim-row-edit">
            <span class="q-badge dim-badge">D{{ di + 1 }}</span>
            <input v-model="dim.label" placeholder="维度名称（含 emoji）" class="dim-label-input" />
            <input v-model="dim.question" placeholder="提问文字" class="dim-q-input" />
            <button class="btn-del" @click="removeDimension(di)">✕</button>
          </div>
        </div>

        <div class="save-bar">
          <button class="btn-primary" @click="save">保存配置</button>
          <span class="save-msg" v-if="saveMsg">{{ saveMsg }}</span>
        </div>
      </div>

      <!-- 数据管理 -->
      <div v-if="activeTab === 'data'" class="tab-content">
        <div class="data-toolbar">
          <button class="btn-primary" @click="exportCSV" :disabled="!results.length">⬇ 导出 CSV</button>
          <button class="btn-ghost" @click="refreshData">↻ 刷新</button>
          <button class="btn-danger" @click="handleClear" :disabled="!results.length">🗑 清空数据</button>
          <span class="data-count" v-if="results.length">共 {{ results.length }} 条</span>
        </div>

        <div v-if="!results.length" class="empty-state">
          <div class="empty-icon">📭</div>
          <p>暂无数据，等待受试者完成问卷</p>
        </div>

        <div v-else class="table-panel">
          <div class="table-scroll">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>图片A</th>
                  <th>图片B</th>
                  <th v-for="dim in config.comparison.dimensions" :key="dim.id">{{ dim.label }}</th>
                  <th v-for="q in config.background.questions" :key="q.id">{{ q.label }}</th>
                  <th>时间</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in results.slice().reverse().slice(0, 100)" :key="r.id">
                  <td class="td-muted">{{ r.id }}</td>
                  <td>{{ r.image_a }}</td>
                  <td>{{ r.image_b }}</td>
                  <td v-for="dim in config.comparison.dimensions" :key="dim.id">
                    <span :class="['sel-tag', r.selections?.[dim.id]]">{{ r.selections?.[dim.id] ?? '-' }}</span>
                  </td>
                  <td v-for="q in config.background.questions" :key="q.id">{{ r.background?.[q.id] ?? '-' }}</td>
                  <td class="td-muted">{{ r.timestamp?.slice(0,19).replace('T',' ') }}</td>
                  <td>
                    <button class="btn-row-del" @click="handleDelete(r.id)" title="删除此条">🗑</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-if="results.length > 100" class="table-note">仅显示最近 100 条，导出 CSV 获取全部</p>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.admin { min-height: 100vh; background: #f0f2f8; font-size: 0.95rem; color: #2d2d3a; }
.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; gap: 1rem; color: #9ca3af; }
.spinner { width: 36px; height: 36px; border: 3px solid #e5e7eb; border-top-color: #4f46e5; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.admin-header { background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 0 2rem; position: sticky; top: 0; z-index: 30; box-shadow: 0 2px 16px rgba(49,46,129,0.35); }
.header-inner { max-width: 1200px; margin: 0 auto; height: 60px; display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 0.9rem; }
.logo-mark { width: 36px; height: 36px; background: rgba(255,255,255,0.15); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
.logo-text { font-weight: 700; color: white; font-size: 1rem; }
.survey-subtitle { font-size: 0.75rem; color: rgba(255,255,255,0.5); }
.header-right { display: flex; align-items: center; gap: 0.5rem; }
.hbtn { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.85); padding: 0.4rem 0.9rem; border-radius: 8px; font-size: 0.85rem; cursor: pointer; text-decoration: none; transition: all 0.2s; }
.hbtn:hover { background: rgba(255,255,255,0.22); color: white; }
.hbtn-danger:hover { background: rgba(239,68,68,0.35); }

.tab-nav { background: white; border-bottom: 1px solid #e5e7eb; display: flex; padding: 0 2rem; overflow-x: auto; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.tab-btn { background: none; border: none; border-bottom: 2px solid transparent; padding: 0.9rem 1.1rem; font-size: 0.9rem; color: #6b7280; cursor: pointer; display: flex; align-items: center; gap: 0.4rem; white-space: nowrap; transition: all 0.2s; }
.tab-btn:hover:not(.active) { color: #374151; background: #f9fafb; }
.tab-btn.active { color: #4f46e5; border-bottom-color: #4f46e5; font-weight: 600; }

.admin-body { max-width: 1000px; margin: 0 auto; padding: 1.8rem 1.5rem; }
.tab-content { display: flex; flex-direction: column; gap: 1.4rem; }

.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.stat-card { background: white; border-radius: 16px; padding: 1.5rem 1.2rem; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #ede9fe; transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-2px); }
.stat-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
.stat-num { font-size: 2.2rem; font-weight: 800; color: #4f46e5; line-height: 1; }
.stat-label { font-size: 0.82rem; color: #9ca3af; margin-top: 0.4rem; }

.panel { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #f0f0f8; }
.panel-title { font-size: 0.95rem; font-weight: 700; color: #374151; margin-bottom: 1.2rem; }
.panel-title-lg { font-size: 1.05rem; font-weight: 700; color: #374151; }
.panel-header-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.2rem; }

.form-row { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem; }
.form-row:last-child { margin-bottom: 0; }
.form-row label { width: 110px; flex-shrink: 0; font-size: 0.88rem; color: #6b7280; font-weight: 500; }
.form-row input:not(.input-sm) { flex: 1; }
input, select { padding: 0.6rem 0.9rem; border: 1.5px solid #e5e7eb; border-radius: 10px; font-size: 0.9rem; background: #fafafa; color: #374151; transition: border-color 0.2s, box-shadow 0.2s; }
input:focus, select:focus { border-color: #4f46e5; outline: none; background: white; box-shadow: 0 0 0 3px rgba(79,70,229,0.1); }
.input-sm { width: 90px; }
.input-hint { color: #9ca3af; font-size: 0.85rem; flex-shrink: 0; }

.cover-preview { margin-top: 0.8rem; border-radius: 10px; overflow: hidden; max-height: 160px; }
.cover-preview img { width: 100%; height: 160px; object-fit: cover; display: block; }

.q-card { background: white; border-radius: 14px; padding: 1.2rem 1.3rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #f0f0f8; margin-bottom: 0.8rem; }
.q-card-top { display: flex; align-items: center; gap: 0.7rem; flex-wrap: wrap; }
.q-badge { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 6px; flex-shrink: 0; }
.dim-badge { background: linear-gradient(135deg, #0891b2, #0e7490); }
.q-input { flex: 1; min-width: 140px; }
.q-select { width: 110px; }
.q-check { display: flex; align-items: center; gap: 0.3rem; font-size: 0.85rem; color: #6b7280; white-space: nowrap; cursor: pointer; }
.q-check input { width: auto; padding: 0; border: none; box-shadow: none; background: none; }

.opts-wrap { margin-top: 1rem; padding-top: 1rem; border-top: 1px dashed #e5e7eb; padding-left: 1.5rem; }
.opt-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.opt-dot { color: #9ca3af; font-size: 1.2rem; flex-shrink: 0; }
.opt-input { flex: 2; }
.opt-val { flex: 1; max-width: 110px; }

.dim-row-edit { display: flex; align-items: center; gap: 0.7rem; margin-top: 0.8rem; }
.dim-label-input { width: 180px; }
.dim-q-input { flex: 1; }

.btn-primary { padding: 0.65rem 1.6rem; background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; border: none; border-radius: 10px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 8px rgba(79,70,229,0.3); }
.btn-primary:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.btn-primary:disabled { background: #d1d5db; box-shadow: none; cursor: not-allowed; }
.btn-ghost { padding: 0.65rem 1.3rem; background: white; border: 1.5px solid #e5e7eb; border-radius: 10px; font-size: 0.9rem; color: #6b7280; cursor: pointer; transition: all 0.2s; }
.btn-ghost:hover { border-color: #4f46e5; color: #4f46e5; }
.btn-danger { padding: 0.65rem 1.3rem; background: white; border: 1.5px solid #fca5a5; border-radius: 10px; font-size: 0.9rem; color: #ef4444; cursor: pointer; transition: all 0.2s; }
.btn-danger:hover:not(:disabled) { background: #ef4444; color: white; }
.btn-danger:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-add { padding: 0.5rem 1rem; background: #eef2ff; border: 1.5px solid #c7d2fe; border-radius: 8px; color: #4f46e5; font-size: 0.88rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-add:hover { background: #4f46e5; color: white; border-color: #4f46e5; }
.btn-add-opt { padding: 0.35rem 0.8rem; background: none; border: 1px dashed #d1d5db; border-radius: 6px; color: #9ca3af; font-size: 0.82rem; cursor: pointer; margin-top: 0.3rem; }
.btn-add-opt:hover { border-color: #4f46e5; color: #4f46e5; }
.btn-del { background: none; border: none; color: #d1d5db; font-size: 0.95rem; cursor: pointer; padding: 0.2rem 0.4rem; border-radius: 6px; flex-shrink: 0; transition: all 0.15s; }
.btn-del:hover { color: #ef4444; background: #fef2f2; }
.btn-del-sm { background: none; border: none; color: #d1d5db; cursor: pointer; font-size: 0.85rem; padding: 0.1rem 0.3rem; }
.btn-del-sm:hover { color: #ef4444; }

.save-bar { display: flex; align-items: center; gap: 1rem; padding: 0.5rem 0; }
.save-msg { color: #10b981; font-size: 0.88rem; font-weight: 600; }

.data-toolbar { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; }
.data-count { margin-left: auto; color: #9ca3af; font-size: 0.88rem; }

.empty-state { background: white; border-radius: 16px; padding: 4rem 2rem; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state p { color: #9ca3af; }
.empty-hint { color: #9ca3af; font-size: 0.88rem; padding: 1.5rem 0; text-align: center; }

.table-panel { background: white; border-radius: 16px; padding: 1.2rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.table-scroll { overflow-x: auto; border-radius: 10px; border: 1px solid #f0f0f8; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.data-table th { background: #f8f9ff; padding: 0.65rem 0.9rem; text-align: left; font-weight: 600; color: #6b7280; border-bottom: 1px solid #e5e7eb; white-space: nowrap; }
.data-table td { padding: 0.6rem 0.9rem; border-bottom: 1px solid #f3f4f6; color: #374151; white-space: nowrap; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #f8f9ff; }
.td-muted { color: #9ca3af; font-size: 0.8rem; }
.sel-tag { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 5px; font-size: 0.8rem; font-weight: 600; }
.sel-tag.a { background: #dbeafe; color: #1d4ed8; }
.sel-tag.b { background: #fef3c7; color: #b45309; }
.sel-tag.tie { background: #f3f4f6; color: #6b7280; }
.table-note { color: #9ca3af; font-size: 0.8rem; text-align: center; margin-top: 0.8rem; }
.btn-row-del { background: none; border: none; color: #d1d5db; font-size: 0.9rem; cursor: pointer; padding: 0.2rem 0.4rem; border-radius: 4px; transition: all 0.15s; }
.btn-row-del:hover { color: #ef4444; background: #fef2f2; }

@media (max-width: 640px) {
  .admin-body { padding: 1rem; }
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .header-right { display: none; }
}
</style>
