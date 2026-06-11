<template>

  <div class="book-node" :class="`book-node--${variant}`" :style="nodeStyle">

    <div class="node-core">

      <span v-if="variant === 'spine'" class="spine-pages" aria-hidden="true" />

      <h3 class="node-title">{{ title }}</h3>

      <p v-if="author" class="node-author">{{ author }}</p>

      <span v-if="showCount && quoteCount" class="node-count">{{ quoteCount }}</span>

    </div>

  </div>

</template>



<script>

const HUB_COLORS = [

  'var(--glt-book-0)',

  'var(--glt-book-1)',

  'var(--glt-book-2)',

  'var(--glt-book-3)',

  'var(--glt-book-4)',

  'var(--glt-book-5)',

  'var(--glt-book-6)',

  'var(--glt-book-7)',

]



export default {

  name: 'BookNode',

  props: {

    title: { type: String, required: true },

    author: { type: String, default: '' },

    quoteCount: { type: Number, default: 0 },

    colorIndex: { type: Number, default: 0 },

    showCount: { type: Boolean, default: false },

    variant: {

      type: String,

      default: 'spine',

      validator: (v) => ['spine', 'footer'].includes(v),

    },

  },

  computed: {

    hubColor() {

      return HUB_COLORS[this.colorIndex % HUB_COLORS.length]

    },

    nodeStyle() {

      return {

        '--hub-color': this.hubColor,

      }

    },

  },

}

</script>



<style scoped>

.book-node {

  position: relative;

}



.book-node--spine {

  width: var(--glt-spine-width);

  z-index: 3;

}



.node-core {

  position: relative;

  display: flex;

  flex-direction: column;

  justify-content: flex-end;

  overflow: hidden;

  transition:

    transform 0.4s var(--glt-ease),

    box-shadow var(--glt-duration);

}



.book-node--spine .node-core {

  width: 100%;

  height: var(--glt-spine-height);

  padding: 12px 10px 14px;

  border-radius: 4px 6px 4px 4px;

  background: linear-gradient(

    135deg,

    color-mix(in srgb, var(--hub-color) 88%, #fff) 0%,

    var(--hub-color) 55%,

    color-mix(in srgb, var(--hub-color) 75%, #3d3429) 100%

  );

  border: 1px solid color-mix(in srgb, var(--hub-color) 60%, #3d3429);

  box-shadow:

    3px 4px 12px rgba(61, 52, 41, 0.18),

    inset 2px 0 6px rgba(255, 255, 255, 0.2),

    inset -3px 0 8px rgba(0, 0, 0, 0.12);

}



.book-node--spine:hover .node-core,

.book-node.is-pulled .node-core {

  transform: translateY(-6px) rotate(-2deg);

  box-shadow:

    6px 10px 20px rgba(61, 52, 41, 0.22),

    inset 2px 0 6px rgba(255, 255, 255, 0.25);

}



.spine-pages {

  position: absolute;

  left: 3px;

  top: 8px;

  bottom: 8px;

  width: 4px;

  border-radius: 1px;

  background: repeating-linear-gradient(

    180deg,

    rgba(255, 255, 255, 0.5) 0px,

    rgba(255, 255, 255, 0.5) 1px,

    transparent 1px,

    transparent 3px

  );

  opacity: 0.6;

}



.node-title {

  margin: 0;

  font-size: var(--glt-text-book-title);

  font-weight: 700;

  line-height: 1.45;

  letter-spacing: -0.02em;

  color: #fff;

  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);

  word-break: keep-all;

  overflow-wrap: break-word;

  display: -webkit-box;

  -webkit-line-clamp: 6;

  -webkit-box-orient: vertical;

  overflow: hidden;

}



.node-author {

  margin: 6px 0 0;

  font-size: var(--glt-text-book-author);

  line-height: 1.35;

  color: rgba(255, 255, 255, 0.85);

  word-break: keep-all;

  display: -webkit-box;

  -webkit-line-clamp: 2;

  -webkit-box-orient: vertical;

  overflow: hidden;

}



.node-count {

  position: absolute;

  top: 6px;

  right: 6px;

  min-width: 20px;

  height: 20px;

  padding: 0 5px;

  display: grid;

  place-items: center;

  border-radius: var(--glt-radius-full);

  font-size: 0.72rem;

  font-weight: 700;

  color: var(--hub-color);

  background: #fff;

  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);

}



.book-node--footer .node-core {

  flex-direction: row;

  align-items: flex-start;

  width: 100%;

  padding: 12px 14px;

  border-radius: var(--glt-radius-md);

  background: var(--glt-surface-raised);

  border: 1.5px solid var(--glt-glass-border);

  gap: 10px;

  text-align: left;

}

</style>

