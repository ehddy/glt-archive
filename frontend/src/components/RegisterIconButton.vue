<template>
  <button
    class="register-icon-btn"
    :class="{ 'register-icon-btn--large': large }"
    :type="type"
    :disabled="disabled"
    :aria-label="label"
    @click="$emit('click', $event)"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 7v10M7 12h10"
        fill="none"
        stroke="currentColor"
        stroke-width="1.85"
        stroke-linecap="round"
      />
    </svg>
  </button>
</template>

<script>
export default {
  name: 'RegisterIconButton',
  props: {
    label: { type: String, default: '포스팅' },
    type: { type: String, default: 'button' },
    disabled: { type: Boolean, default: false },
    large: { type: Boolean, default: false },
  },
  emits: ['click'],
}
</script>

<style scoped>
.register-icon-btn {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 50%;
  background: var(--glt-accent);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(95, 143, 122, 0.22);
  transition: background var(--glt-duration), opacity var(--glt-duration);
}

.register-icon-btn--large {
  width: 48px;
  height: 48px;
}

.register-icon-btn:hover:not(:disabled) {
  background: var(--glt-accent-hover);
}

.register-icon-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.register-icon-btn svg {
  width: 18px;
  height: 18px;
  display: block;
}

.register-icon-btn--large svg {
  width: 22px;
  height: 22px;
}
</style>
