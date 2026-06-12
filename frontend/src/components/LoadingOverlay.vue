<template>

  <div class="page-loading" role="status" aria-live="polite" aria-busy="true" aria-label="로딩 중">

    <div
      class="page-loading-card glt-card"
      :class="{ 'page-loading-card--with-text': message }"
    >
      <div class="page-loading-visual" aria-hidden="true">
        <span class="page-loading-ring" />
      </div>

      <p v-if="message" class="page-loading-text">{{ message }}</p>

      <div class="page-loading-dots" aria-hidden="true">

        <span />

        <span />

        <span />

      </div>

    </div>

  </div>

</template>



<script>

export default {
  name: 'LoadingOverlay',
  props: {
    message: { type: String, default: '' },
  },
}

</script>



<style scoped>

.page-loading {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  padding: var(--glt-space-4);
  background: transparent;
  pointer-events: all;
  touch-action: none;
}

.page-loading-card {
  width: min(100%, 120px);
  padding: 24px 20px 20px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(61, 52, 41, 0.14);
  animation: loading-card-in 0.32s var(--glt-ease);
}

.page-loading-card--with-text {
  width: min(100%, 220px);
  padding: 28px 24px 22px;
}

[data-theme='night'] .page-loading-card {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}

.page-loading-text {
  margin: 14px 0 0;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--glt-ink-secondary);
  line-height: 1.45;
}



.page-loading-visual {

  position: relative;

  width: 56px;

  height: 56px;

  margin: 0 auto;

}



.page-loading-ring {

  position: absolute;

  inset: 0;

  border-radius: 50%;

  border: 2px solid var(--glt-glass-border);

  border-top-color: var(--glt-accent);

  border-right-color: var(--glt-accent-muted);

  animation: spin 0.9s linear infinite;

}



.page-loading-dots {

  display: flex;

  justify-content: center;

  gap: 6px;

  margin-top: 14px;

}



.page-loading-dots span {

  width: 6px;

  height: 6px;

  border-radius: 50%;

  background: var(--glt-accent-muted);

  animation: loading-dot 1.1s ease-in-out infinite;

}



.page-loading-dots span:nth-child(2) {

  animation-delay: 0.15s;

}



.page-loading-dots span:nth-child(3) {

  animation-delay: 0.3s;

}



@keyframes spin {

  to { transform: rotate(360deg); }

}



@keyframes loading-dot {

  0%, 80%, 100% { opacity: 0.35; transform: translateY(0); }

  40% { opacity: 1; transform: translateY(-3px); }

}



@keyframes loading-card-in {

  from {

    opacity: 0;

    transform: translateY(8px) scale(0.98);

  }

  to {

    opacity: 1;

    transform: translateY(0) scale(1);

  }

}

</style>

