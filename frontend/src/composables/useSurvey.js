const DEFAULT_CONFIG = {
  title: "街道环境偏好研究",
  description: "本调查仅用于学术研究，不会泄露您的个人隐私",
  coverImage: "",
  background: {
    title: "背景调查",
    questions: [
      {
        id: "age", label: "您的年龄段", type: "select", required: true,
        options: [
          { value: "18-25", label: "18-25岁" },
          { value: "26-35", label: "26-35岁" },
          { value: "36-60", label: "36-60岁" },
          { value: "60+",   label: "60岁及以上" }
        ]
      },
      {
        id: "gender", label: "您的性别", type: "radio", required: true,
        options: [
          { value: "male",   label: "男" },
          { value: "female", label: "女" }
        ]
      },
      {
        id: "experience", label: "您的自行车使用频率", type: "select", required: true,
        options: [
          { value: "5+",  label: "每周5次以上" },
          { value: "3-5", label: "每周3-5次" },
          { value: "1-3", label: "每周1-3次" },
          { value: "0",   label: "几乎不骑" }
        ]
      },
      {
        id: "work", label: "您从事什么职业", type: "select", required: true,
        options: [
          { value: "student",   label: "学生" },
          { value: "employed",  label: "固定职业" },
          { value: "freelance", label: "自由职业" },
          { value: "other",     label: "非在职人员" }
        ]
      }
    ]
  },
  comparison: {
    instruction: "请对两张图片在以下各维度分别做出选择",
    totalCount: 10,
    imageRange: { min: 1, max: 20 },
    dimensions: [
      { id: "safety",     label: "🛡️ 安全 (Safety)",     question: "在这条街上走动感觉有多安全？" },
      { id: "beauty",     label: "🌸 美丽 (Beauty)",      question: "这条街看起来有多美？" },
      { id: "liveliness", label: "⚡ 活力 (Liveliness)",  question: "这条街看起来有多繁华、有活力？" },
      { id: "wealth",     label: "💰 富裕 (Wealth)",      question: "这条街看起来有多富裕？" },
      { id: "boring",     label: "😐 无聊 (Boring)",      question: "这条街看起来有多单调乏味？" },
      { id: "depressing", label: "😔 压抑 (Depressing)",  question: "这条街看起来有多令人压抑？" }
    ]
  }
}

const CONFIG_KEY = 'scenerank_config'
const RESULTS_KEY = 'scenerank_results'

export function useSurveyConfig() {
  const loadConfig = async () => {
    const raw = localStorage.getItem(CONFIG_KEY)
    return raw ? JSON.parse(raw) : DEFAULT_CONFIG
  }

  const saveConfig = async (config) => {
    localStorage.setItem(CONFIG_KEY, JSON.stringify(config))
  }

  const resetConfig = async () => {
    localStorage.removeItem(CONFIG_KEY)
    return DEFAULT_CONFIG
  }

  return { loadConfig, saveConfig, resetConfig }
}

export function useSurveyResults() {
  const loadResults = async () => {
    const raw = localStorage.getItem(RESULTS_KEY)
    return raw ? JSON.parse(raw) : []
  }

  const clearResults = async () => {
    localStorage.removeItem(RESULTS_KEY)
  }

  const deleteResult = async (id) => {
    const results = JSON.parse(localStorage.getItem(RESULTS_KEY) || '[]')
    const updated = results.filter(r => r.id !== id)
    localStorage.setItem(RESULTS_KEY, JSON.stringify(updated))
  }

  const submitResult = async (record) => {
    const results = JSON.parse(localStorage.getItem(RESULTS_KEY) || '[]')
    results.push({ ...record, id: Date.now() + Math.random() })
    localStorage.setItem(RESULTS_KEY, JSON.stringify(results))
  }

  const exportCSV = async () => {
    const results = JSON.parse(localStorage.getItem(RESULTS_KEY) || '[]')
    if (!results.length) return alert('暂无数据')
    const first = results[0]
    const dimKeys = Object.keys(first.selections || {})
    const bgKeys = Object.keys(first.background || {})
    const headers = ['id', 'image_a', 'image_b', ...dimKeys.map(d => `sel_${d}`), ...bgKeys, 'timestamp']
    const rows = results.map(r => [
      r.id, r.image_a, r.image_b,
      ...dimKeys.map(d => r.selections?.[d] ?? ''),
      ...bgKeys.map(k => r.background?.[k] ?? ''),
      r.timestamp
    ])
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `scenerank_demo.csv`; a.click()
    URL.revokeObjectURL(url)
  }

  return { loadResults, clearResults, deleteResult, submitResult, exportCSV }
}
