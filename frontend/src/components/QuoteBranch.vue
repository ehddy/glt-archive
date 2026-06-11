<template>
  <router-link :to="`/quotes/${quote.id}`" class="quote-branch glt-card-raised">
    <p class="glt-quote">{{ quote.text }}</p>
  </router-link>
</template>

<script>
export default {
  name: 'QuoteBranch',
  props: {
    quote: { type: Object, required: true },
  },
}
</script>

<style scoped>
.quote-branch {
  display: block;
  padding: var(--glt-space-4) var(--glt-space-5);
  text-decoration: none;
  transition: transform var(--glt-duration) var(--glt-ease), box-shadow var(--glt-duration), border-color var(--glt-duration);
  border-color: rgba(212, 203, 184, 0.5);
}

.quote-branch:hover {
  transform: translateX(4px);
  box-shadow: var(--glt-shadow-md);
  border-color: var(--glt-accent-muted);
}

.quote-branch .glt-quote {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
