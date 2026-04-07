<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  config: { type: Object, required: true }
})
const emit = defineEmits(['submit'])

const answers = ref(Object.fromEntries(props.config.questions.map(q => [q.id, ''])))

const allAnswered = computed(() =>
  props.config.questions.filter(q => q.required).every(q => answers.value[q.id] !== '')
)

const handleSubmit = () => {
  if (!allAnswered.value) return
  emit('submit', { ...answers.value })
}
</script>

<template>
  <div class="bg-form">
    <div class="form-card">
      <div class="form-header">
        <div class="form-icon">📋</div>
        <h2>{{ config.title || '背景调查' }}</h2>
        <p>请如实填写以下信息，所有数据仅用于学术研究</p>
      </div>

      <div class="questions">
        <div v-for="(q, idx) in config.questions" :key="q.id" class="question-item">
          <div class="q-label">
            <span class="q-index">{{ idx + 1 }}</span>
            {{ q.label }}
            <span v-if="q.required" class="required">*</span>
          </div>

          <!-- 下拉 -->
          <select v-if="q.type === 'select'" v-model="answers[q.id]" class="q-select">
            <option value="">请选择...</option>
            <option v-for="opt in q.options" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>

          <!-- 单选 -->
          <div v-else-if="q.type === 'radio'" class="radio-group">
            <label v-for="opt in q.options" :key="opt.value"
              class="radio-item" :class="{ selected: answers[q.id] === opt.value }">
              <input type="radio" :name="q.id" :value="opt.value" v-model="answers[q.id]" />
              {{ opt.label }}
            </label>
          </div>

          <!-- 文本 -->
          <input v-else-if="q.type === 'text'" type="text"
            v-model="answers[q.id]" :placeholder="q.placeholder || '请输入'" class="q-text" />
        </div>
      </div>

      <button class="submit-btn" :disabled="!allAnswered" @click="handleSubmit">
        开始图像对比 →
      </button>
    </div>
  </div>
</template>

<style scoped>
.bg-form {
  min-height: 80vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem 4rem;
}

.form-card {
  background: white;
  border-radius: 24px;
  padding: 2.5rem;
  width: 100%;
  max-width: 620px;
  box-shadow: 0 8px 40px rgba(79,70,229,0.1);
  border: 1px solid #ede9fe;
}

.form-header {
  text-align: center;
  margin-bottom: 2.5rem;
}
.form-icon { font-size: 2.5rem; margin-bottom: 0.8rem; }
.form-header h2 { font-size: 1.5rem; font-weight: 700; color: #1e1b4b; margin-bottom: 0.4rem; }
.form-header p { color: #9ca3af; font-size: 0.9rem; }

.questions { display: flex; flex-direction: column; gap: 1.6rem; }

.question-item { display: flex; flex-direction: column; gap: 0.7rem; }

.q-label {
  display: flex; align-items: center; gap: 0.5rem;
  font-weight: 600; font-size: 0.95rem; color: #374151;
}
.q-index {
  width: 24px; height: 24px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700; flex-shrink: 0;
}
.required { color: #ef4444; font-size: 0.85rem; }

.q-select, .q-text {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  font-size: 0.95rem;
  background: #fafafa;
  color: #374151;
  transition: all 0.2s;
  appearance: auto;
}
.q-select:focus, .q-text:focus {
  border-color: #4f46e5;
  outline: none;
  background: white;
  box-shadow: 0 0 0 3px rgba(79,70,229,0.1);
}

.radio-group { display: flex; flex-wrap: wrap; gap: 0.6rem; }
.radio-item {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.55rem 1.1rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.9rem; color: #6b7280;
  cursor: pointer; transition: all 0.2s;
  background: #fafafa;
}
.radio-item input { display: none; }
.radio-item:hover { border-color: #a5b4fc; color: #4f46e5; background: #eef2ff; }
.radio-item.selected { border-color: #4f46e5; color: #4f46e5; background: #eef2ff; font-weight: 600; }

.submit-btn {
  width: 100%;
  margin-top: 2.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 16px rgba(79,70,229,0.35);
  letter-spacing: 0.02em;
}
.submit-btn:hover:not(:disabled) {
  opacity: 0.92;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79,70,229,0.45);
}
.submit-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  box-shadow: none;
  cursor: not-allowed;
}
</style>
