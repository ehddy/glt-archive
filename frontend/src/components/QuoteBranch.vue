<template>

  <router-link

    :to="`/quotes/${quote.id}`"

    class="quote-bubble"

    :class="bubbleClasses"

  >

    <p class="glt-quote">{{ quote.text }}</p>

  </router-link>

</template>



<script>

export default {

  name: 'QuoteBranch',

  props: {

    quote: { type: Object, required: true },

    tailDirection: {

      type: String,

      default: 'bottom',

      validator: (v) => ['top', 'bottom', 'left', 'right'].includes(v),

    },

    variant: {

      type: String,

      default: 'shelf',

      validator: (v) => ['shelf', 'graph', 'card', 'spread'].includes(v),

    },

    highlighted: { type: Boolean, default: false },

  },

  computed: {

    bubbleClasses() {

      const extra = this.highlighted ? ['quote-bubble--highlight'] : []

      if (this.variant === 'card') return ['quote-bubble--card', ...extra]

      if (this.variant === 'spread') return ['quote-bubble--spread', ...extra]

      if (this.variant === 'graph') {

        return ['quote-bubble--graph', `tail-${this.tailDirection}`, ...extra]

      }

      return ['quote-bubble--shelf', `tail-${this.tailDirection}`, ...extra]

    },

  },

}

</script>



<style scoped>

.quote-bubble {

  position: relative;

  display: block;

  text-decoration: none;

  transition:

    transform var(--glt-duration) var(--glt-ease),

    box-shadow var(--glt-duration),

    border-color var(--glt-duration);

}



.quote-bubble--shelf {

  width: 100%;

  max-width: var(--glt-bubble-shelf-width);

  padding: 14px 16px;

  background: var(--glt-bubble-bg);

  border: 1px solid var(--glt-bubble-border);

  border-radius: 12px 12px 12px 4px;

  box-shadow: var(--glt-bubble-shadow);

}



.quote-bubble--shelf:hover {

  transform: translateY(-2px);

  border-color: color-mix(in srgb, var(--hub-color, var(--glt-accent)) 35%, var(--glt-bubble-border));

  box-shadow: var(--glt-shadow-md);

}



.quote-bubble--spread {
  width: 100%;
  padding: 12px 14px;
  background: var(--glt-surface-raised);
  border: 1px solid var(--glt-glass-border);
  border-radius: var(--glt-radius-sm);
  box-shadow: var(--glt-shadow-sm);
}

.quote-bubble--spread:hover {
  border-color: color-mix(in srgb, var(--glt-accent) 30%, var(--glt-glass-border));
  box-shadow: var(--glt-shadow-md);
}

.quote-bubble--spread .glt-quote {
  font-family: var(--glt-font-sans);
  font-size: 0.88rem;
  font-weight: 400;
  line-height: 1.65;
  letter-spacing: -0.02em;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.quote-bubble--graph {

  width: var(--glt-bubble-graph-width);

  padding: 11px 13px;

  background: var(--glt-bubble-bg);

  border: 1.5px solid var(--glt-bubble-border);

  border-radius: var(--glt-radius-bubble);

  box-shadow: var(--glt-shadow-md);

}

.quote-bubble--graph:hover {
  transform: translateY(-2px) scale(1.02);
  border-color: color-mix(in srgb, var(--hub-color, var(--glt-accent)) 40%, var(--glt-bubble-border));
}



.quote-bubble--card {

  width: 100%;

  padding: 12px 14px;

  background: var(--glt-bubble-bg);

  border: 1px solid var(--glt-bubble-border);

  border-radius: var(--glt-radius-md);

  cursor: pointer;

}

.quote-bubble--card:hover {
  border-color: color-mix(in srgb, var(--glt-accent) 35%, var(--glt-bubble-border));
  box-shadow: var(--glt-shadow-sm);
}

.quote-bubble--card .glt-quote {
  font-size: 0.92rem;
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}



.quote-bubble .glt-quote {

  margin: 0;

  font-size: var(--glt-text-quote);

  font-weight: 500;

  line-height: 1.7;

  color: var(--glt-ink);

  word-break: keep-all;

  overflow-wrap: break-word;

}



.quote-bubble--graph .glt-quote {

  display: -webkit-box;

  -webkit-line-clamp: 6;

  -webkit-box-orient: vertical;

  overflow: hidden;

}

.quote-bubble--highlight {
  border-color: color-mix(in srgb, var(--glt-accent) 45%, var(--glt-bubble-border));
  background: color-mix(in srgb, var(--glt-accent-soft) 35%, #fff);
  box-shadow: var(--glt-shadow-md);
}



/* Tails */

.tail-bottom::before {

  bottom: -8px;

  left: 18px;

  border-width: 8px 8px 0;

  border-top-color: var(--glt-bubble-border);

}

.tail-bottom::after {

  bottom: -6px;

  left: 19px;

  border-width: 6px 6px 0;

  border-top-color: var(--glt-bubble-bg);

}



.tail-top::before {

  top: -8px;

  left: 50%;

  margin-left: -8px;

  border-width: 0 8px 8px;

  border-bottom-color: var(--glt-bubble-border);

}

.tail-top::after {

  top: -6px;

  left: 50%;

  margin-left: -6px;

  border-width: 0 6px 6px;

  border-bottom-color: var(--glt-bubble-bg);

}



.tail-left::before {

  left: -8px;

  top: 50%;

  margin-top: -8px;

  border-width: 8px 8px 8px 0;

  border-right-color: var(--glt-bubble-border);

}

.tail-left::after {

  left: -6px;

  top: 50%;

  margin-top: -6px;

  border-width: 6px 6px 6px 0;

  border-right-color: var(--glt-bubble-bg);

}



.tail-right::before {

  right: -8px;

  top: 50%;

  margin-top: -8px;

  border-width: 8px 0 8px 8px;

  border-left-color: var(--glt-bubble-border);

}

.tail-right::after {

  right: -6px;

  top: 50%;

  margin-top: -6px;

  border-width: 6px 0 6px 6px;

  border-left-color: var(--glt-bubble-bg);

}



.quote-bubble::before,

.quote-bubble::after {

  content: '';

  position: absolute;

  border: solid transparent;

  pointer-events: none;

}

</style>

