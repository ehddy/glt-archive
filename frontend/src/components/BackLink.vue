<template>
  <router-link :to="to" class="back-link" :aria-label="label">
    <svg class="back-link-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M14.5 6.5L9 12l5.5 5.5"
        fill="none"
        stroke="currentColor"
        stroke-width="1.75"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </router-link>
</template>

<script>
export default {
  name: 'BackLink',
  props: {
    to: { type: [String, Object], required: true },
    label: { type: String, required: true },
  },
}
</script>
