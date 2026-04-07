<script setup>
import { ref, onMounted } from 'vue'
import { useSurveyConfig, useSurveyResults } from '../composables/useSurvey.js'
import BackgroundForm from '../components/BackgroundForm.vue'
import ImageComparison from '../components/ImageComparison.vue'
import CompletePage from '../components/CompletePage.vue'

const { loadConfig } = useSurveyConfig()
const { submitResult } = useSurveyResults()

const stage = ref('loading')
const config = ref(null)
const backgroundAnswers = ref(null)
const finalCount = ref(0)

onMounted(async () => {
  config.value = await loadConfig()
  stage.value = 'background'
})

const onBackgroundSubmit = (answers) => {
  backgroundAnswers.value = answers
  stage.value = 'comparison'
}

const onComplete = async (records) => {
  for (const r of records) {
    await submitResult(r)
  }
  finalCount.value = records.length
  stage.value = 'complete'
}

const onRestart = async () => {
  backgroundAnswers.value = null
  config.value = await loadConfig()
  stage.value = 'background'
}
</script>

<template>
  <div class="survey-root" :style="config?.coverImage ? {
    backgroundImage: `url(${config.coverImage})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed'
  } : {}">
    <div v-if="config?.coverImage" class="bg-overlay"></div>
    <div class="survey-content">
      <div v-if="stage === 'loading'" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      <template v-else-if="stage === 'background'">
        <div class="survey-header" :class="{ 'has-bg': config.coverImage }">
          <h1>{{ config.title }}</h1>
          <p>{{ config.description }}</p>
        </div>
        <BackgroundForm :config="config.background" @submit="onBackgroundSubmit" />
      </template>
      <ImageComparison
        v-else-if="stage === 'comparison'"
        :config="config.comparison"
        :background="backgroundAnswers"
        @complete="onComplete"
      />
      <CompletePage
        v-else-if="stage === 'complete'"
        :count="finalCount"
        @restart="onRestart"
      />
    </div>
  </div>
</template>

<style scoped>
.survey-root { min-height: 100vh; position: relative; }
.bg-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 0; }
.survey-content { position: relative; z-index: 1; }
.loading {
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  height: 100vh; gap: 1rem; color: #9ca3af;
}
.spinner {
  width: 36px; height: 36px;
  border: 3px solid #e5e7eb;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.survey-header { text-align: center; padding: 2.5rem 1rem 0; }
.survey-header h1 { font-size: 1.9rem; font-weight: 700; color: #1e1b4b; margin-bottom: 0.4rem; }
.survey-header p { color: #6b7280; font-size: 0.95rem; }
.survey-header.has-bg h1 { color: white; text-shadow: 0 2px 8px rgba(0,0,0,0.4); }
.survey-header.has-bg p { color: rgba(255,255,255,0.85); }
</style>
