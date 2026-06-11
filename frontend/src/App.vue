<template>
  <div class="app">
    <div class="app-bg" aria-hidden="true">
      <div class="app-bg-grid" />
    </div>

    <header class="header">
      <div class="glt-container header-inner">
        <router-link to="/" class="brand">
          <span class="brand-mark">G</span>
          <div class="brand-text">
            <strong>괴테는 모든 것을 말했다</strong>
            <p>작품에서 뻗어 나온 구절들</p>
          </div>
        </router-link>
        <nav class="nav">
          <router-link to="/" class="nav-link">탐색</router-link>
          <router-link to="/register" class="nav-link nav-link-cta">구절 등록</router-link>
        </nav>
      </div>
    </header>

    <main class="main glt-container">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  position: relative;
}

.app-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: var(--glt-bg);
  pointer-events: none;
}

.app-bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 1px 1px, var(--glt-line) 1px, transparent 0);
  background-size: 28px 28px;
  opacity: 0.35;
}

.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(243, 239, 230, 0.82);
  backdrop-filter: blur(16px) saturate(1.2);
  border-bottom: 1px solid var(--glt-line);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--glt-space-6);
  padding: var(--glt-space-4) 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--glt-space-3);
  text-decoration: none;
}

.brand-mark {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: var(--glt-radius-sm);
  background: var(--glt-accent);
  color: #fff;
  font-family: var(--glt-font-serif);
  font-size: 1.1rem;
  font-weight: 700;
  box-shadow: var(--glt-shadow-sm);
}

.brand-text strong {
  display: block;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--glt-ink);
}

.brand-text p {
  margin: 1px 0 0;
  font-size: 0.75rem;
  color: var(--glt-ink-tertiary);
}

.nav {
  display: flex;
  align-items: center;
  gap: var(--glt-space-2);
}

.nav-link {
  padding: 8px 14px;
  border-radius: var(--glt-radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--glt-ink-secondary);
  text-decoration: none;
  transition: all var(--glt-duration) var(--glt-ease);
}

.nav-link:hover {
  color: var(--glt-ink);
  background: var(--glt-overlay);
}

.nav-link.router-link-active {
  color: var(--glt-accent);
  background: var(--glt-accent-soft);
}

.nav-link-cta.router-link-active,
.nav-link-cta {
  background: var(--glt-accent);
  color: #fff;
}

.nav-link-cta:hover {
  background: var(--glt-accent-hover);
  color: #fff;
}

.main {
  position: relative;
  z-index: 1;
  padding: var(--glt-space-10) 0 var(--glt-space-12);
}
</style>
