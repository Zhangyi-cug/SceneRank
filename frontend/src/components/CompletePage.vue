<script setup>
defineProps({ count: { type: Number, required: true } })
const emit = defineEmits(['restart'])
</script>

<template>
  <div class="complete-page">
    <div class="confetti">🎊</div>
    <div class="card">
      <div class="check-circle">✓</div>
      <h2>感谢您的参与！</h2>
      <p>您已完成 <strong>{{ count }}</strong> 对图像的对比评价</p>
      <p class="sub">您的回答已记录，对本研究非常有帮助。</p>
      <button class="btn-restart" @click="emit('restart')">再做一次</button>
    </div>
  </div>
</template>

<style scoped>
.complete-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}
.confetti {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: bounce 1s ease infinite alternate;
}
@keyframes bounce {
  from { transform: translateY(0); }
  to   { transform: translateY(-12px); }
}
.card {
  background: white;
  border-radius: 24px;
  padding: 3rem 2.5rem;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  max-width: 420px;
  width: 100%;
}
.check-circle {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
  margin: 0 auto 1.5rem;
}
h2 { font-size: 1.8rem; margin-bottom: 0.6rem; color: #1a1a2e; }
p { color: #666; margin-bottom: 0.4rem; }
.sub { font-size: 0.9rem; color: #aaa; margin-bottom: 2rem; }
.btn-restart {
  width: 100%;
  padding: 0.9rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}
.btn-restart:hover { opacity: 0.9; transform: translateY(-2px); }
</style>
