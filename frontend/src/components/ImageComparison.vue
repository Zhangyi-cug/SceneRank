<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  config: { type: Object, required: true },
  background: { type: Object, required: true }
})
const emit = defineEmits(['complete'])

const { imageRange, dimensions, totalCount, instruction } = props.config

const genPair = () => {
  const { min, max } = imageRange
  let a = Math.floor(Math.random() * (max - min + 1)) + min
  let b
  do { b = Math.floor(Math.random() * (max - min + 1)) + min } while (b === a)
  return { a, b }
}

const images = ref(genPair())
const compareCount = ref(0)
const isCooldown = ref(false)
const isPortrait = ref(false)
const records = ref([])
const currentSelections = ref(Object.fromEntries(dimensions.map(d => [d.id, null])))
const activeDimIdx = ref(0)

const allDimensionsSelected = computed(() =>
  dimensions.every(d => currentSelections.value[d.id] !== null)
)
const progress = computed(() => (compareCount.value / totalCount) * 100)
const getImageUrl = (id) => `images/${id}.jpg`

const checkOrientation = () => { isPortrait.value = window.innerWidth < 768 }

const selectDimension = (dimId, side) => {
  if (isCooldown.value) return
  currentSelections.value[dimId] = side
  const nextIdx = dimensions.findIndex(d => currentSelections.value[d.id] === null)
  if (nextIdx !== -1) activeDimIdx.value = nextIdx
}

const nextPair = () => {
  if (!allDimensionsSelected.value) return
  records.value.push({
    image_a: images.value.a,
    image_b: images.value.b,
    selections: { ...currentSelections.value },
    background: props.background,
    timestamp: new Date().toISOString()
  })
  compareCount.value++
  if (compareCount.value >= totalCount) {
    emit('complete', records.value)
    return
  }
  isCooldown.value = true
  setTimeout(() => {
    images.value = genPair()
    currentSelections.value = Object.fromEntries(dimensions.map(d => [d.id, null]))
    activeDimIdx.value = 0
    isCooldown.value = false
  }, 300)
}

const skipPair = () => {
  if (isCooldown.value) return
  images.value = genPair()
  currentSelections.value = Object.fromEntries(dimensions.map(d => [d.id, null]))
  activeDimIdx.value = 0
}

onMounted(() => { checkOrientation(); window.addEventListener('resize', checkOrientation) })
onUnmounted(() => window.removeEventListener('resize', checkOrientation))
</script>

<template>
  <div class="comparison-page">
    <div class="topbar">
      <div class="topbar-inner">
        <div class="progress-info">
          <span class="progress-text">第 <strong>{{ compareCount + 1 }}</strong> / {{ totalCount }} 对</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <button class="btn-skip" @click="skipPair" :disabled="isCooldown">↻ 换一对</button>
      </div>
    </div>

    <div class="images-section" :class="{ portrait: isPortrait }">
      <div class="img-card" :class="{ fading: isCooldown }">
        <img :src="getImageUrl(images.a)" alt="图片A" />
        <div class="img-badge">A</div>
      </div>
      <div class="vs-circle">VS</div>
      <div class="img-card" :class="{ fading: isCooldown }">
        <img :src="getImageUrl(images.b)" alt="图片B" />
        <div class="img-badge">B</div>
      </div>
    </div>

    <div class="rating-section">
      <p class="instruction-text">{{ instruction }}</p>
      <div class="dim-list">
        <div v-for="(dim, idx) in dimensions" :key="dim.id" class="dim-card"
          :class="{ active: idx === activeDimIdx && currentSelections[dim.id] === null, done: currentSelections[dim.id] !== null }">
          <div class="dim-info">
            <div class="dim-name">{{ dim.label }}</div>
            <div class="dim-question">{{ dim.question }}</div>
          </div>
          <div class="dim-choices">
            <button class="choice-btn choice-a" :class="{ selected: currentSelections[dim.id] === 'a' }" @click="selectDimension(dim.id, 'a')">A 更好</button>
            <button class="choice-btn choice-tie" :class="{ selected: currentSelections[dim.id] === 'tie' }" @click="selectDimension(dim.id, 'tie')">相同</button>
            <button class="choice-btn choice-b" :class="{ selected: currentSelections[dim.id] === 'b' }" @click="selectDimension(dim.id, 'b')">B 更好</button>
          </div>
          <div class="done-check" v-if="currentSelections[dim.id] !== null">✓</div>
        </div>
      </div>
      <button class="btn-next" :disabled="!allDimensionsSelected || isCooldown" @click="nextPair">
        {{ compareCount + 1 >= totalCount ? '完成提交 🎉' : '下一对 →' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.comparison-page { min-height: 100vh; background: #f0f2f8; display: flex; flex-direction: column; }
.topbar { background: white; padding: 0.8rem 1.5rem; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.topbar-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; gap: 1rem; }
.progress-info { flex-shrink: 0; }
.progress-text { font-size: 0.9rem; color: #6b7280; }
.progress-text strong { color: #4f46e5; font-size: 1rem; }
.progress-track { flex: 1; height: 8px; background: #e5e7eb; border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #4f46e5, #7c3aed); border-radius: 99px; transition: width 0.5s ease; }
.btn-skip { background: none; border: 1.5px solid #e5e7eb; padding: 0.35rem 0.9rem; border-radius: 20px; font-size: 0.85rem; color: #6b7280; cursor: pointer; white-space: nowrap; transition: all 0.2s; flex-shrink: 0; }
.btn-skip:hover:not(:disabled) { border-color: #4f46e5; color: #4f46e5; }
.btn-skip:disabled { opacity: 0.4; cursor: not-allowed; }
.images-section { display: grid; grid-template-columns: 1fr 56px 1fr; align-items: center; gap: 1rem; padding: 1.2rem 1.5rem; max-width: 1400px; margin: 0 auto; width: 100%; }
.images-section.portrait { grid-template-columns: 1fr; }
.img-card { position: relative; border-radius: 16px; overflow: hidden; box-shadow: 0 6px 24px rgba(0,0,0,0.12); transition: opacity 0.3s, transform 0.3s; background: #e5e7eb; }
.img-card.fading { opacity: 0.4; transform: scale(0.98); }
.img-card img { width: 100%; display: block; max-height: 44vh; object-fit: cover; }
.img-badge { position: absolute; top: 12px; left: 12px; background: rgba(0,0,0,0.6); color: white; font-weight: 800; font-size: 1rem; padding: 0.25rem 0.75rem; border-radius: 8px; backdrop-filter: blur(4px); }
.vs-circle { width: 48px; height: 48px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem; color: #4f46e5; box-shadow: 0 2px 12px rgba(79,70,229,0.2); flex-shrink: 0; margin: 0 auto; }
.rating-section { max-width: 900px; margin: 0 auto; width: 100%; padding: 0 1.5rem 2.5rem; }
.instruction-text { text-align: center; color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem; }
.dim-list { display: flex; flex-direction: column; gap: 0.7rem; }
.dim-card { display: flex; align-items: center; gap: 1rem; background: white; border-radius: 14px; padding: 1rem 1.2rem; border: 2px solid transparent; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: all 0.2s; position: relative; }
.dim-card.active { border-color: #a5b4fc; box-shadow: 0 4px 16px rgba(79,70,229,0.12); }
.dim-card.done { border-color: #6ee7b7; background: #f0fdf4; }
.dim-info { flex: 1; min-width: 0; }
.dim-name { font-weight: 700; font-size: 0.95rem; color: #374151; }
.dim-question { font-size: 0.82rem; color: #9ca3af; margin-top: 0.15rem; }
.dim-choices { display: flex; gap: 0.5rem; flex-shrink: 0; }
.choice-btn { padding: 0.45rem 1rem; border-radius: 10px; border: 1.5px solid #e5e7eb; background: white; font-size: 0.88rem; font-weight: 600; color: #6b7280; cursor: pointer; transition: all 0.15s; white-space: nowrap; }
.choice-btn:hover { transform: translateY(-1px); }
.choice-a:hover { border-color: #4f46e5; color: #4f46e5; background: #eef2ff; }
.choice-a.selected { background: #4f46e5; border-color: #4f46e5; color: white; box-shadow: 0 2px 8px rgba(79,70,229,0.3); }
.choice-b:hover { border-color: #7c3aed; color: #7c3aed; background: #f5f3ff; }
.choice-b.selected { background: #7c3aed; border-color: #7c3aed; color: white; box-shadow: 0 2px 8px rgba(124,58,237,0.3); }
.choice-tie:hover { border-color: #9ca3af; color: #6b7280; background: #f9fafb; }
.choice-tie.selected { background: #6b7280; border-color: #6b7280; color: white; }
.done-check { position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); color: #10b981; font-size: 1.1rem; font-weight: 700; }
.btn-next { display: block; width: 50%; margin: 1.5rem auto 0; padding: 0.95rem; background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; border: none; border-radius: 14px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 16px rgba(79,70,229,0.35); }
.btn-next:hover:not(:disabled) { opacity: 0.92; transform: translateY(-2px); }
.btn-next:disabled { background: #e5e7eb; color: #9ca3af; box-shadow: none; cursor: not-allowed; transform: none; }
@media (max-width: 640px) {
  .dim-card { flex-direction: column; align-items: flex-start; }
  .dim-choices { width: 100%; }
  .choice-btn { flex: 1; text-align: center; }
  .done-check { top: 1rem; transform: none; }
  .btn-next { width: 85%; }
}
</style>
