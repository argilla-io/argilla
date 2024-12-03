<template>
  <li class="status-counter" :class="{ rainbow }">
    <span>
      <span class="color-bullet" :style="{ backgroundColor: color }"></span>
      <label class="status-counter__name" v-text="statusLabel" />
    </span>
    <span class="status-counter__counter" v-text="value" />
  </li>
</template>

<script>
export default {
  props: {
    color: {
      type: String,
      required: true,
    },
    name: {
      type: String,
      required: true,
    },
    value: {
      type: Number,
      required: true,
    },
    rainbow: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    statusLabel() {
      return this.$tc(`recordStatus.${this.name}`, 1);
    },
  },
};
</script>

<style scoped lang="scss">
$bullet-size: 8px;
.color-bullet {
  display: inline-flex;
  height: $bullet-size;
  width: $bullet-size;
  margin-right: 4px;
  border-radius: $border-radius-rounded;
}
.status-counter {
  display: flex;
  flex-direction: row;
  gap: $base-space;
  padding: $base-space;
  background: var(--bg-opacity-3);
  border-radius: $border-radius;

  &__name {
    text-transform: capitalize;
    color: var(--fg-secondary);
    @include font-size(12px);
  }
  &__counter {
    font-weight: 600;
    color: var(--fg-primary);
    @include font-size(14px);
  }
}

.rainbow {
  position: relative;
  padding: $base-space;
}

.rainbow::before {
  content: "";
  position: absolute;
  top: -2px;
  right: -2px;
  bottom: -2px;
  left: -2px;
  border-radius: $border-radius;
  border: solid 2px transparent;
  border-image: conic-gradient(
      from var(--angle),
      #e70000,
      #ff8c00,
      #ffef00,
      #00811f,
      #3064a9,
      #87189d
    )
    1;
  animation: 2s rotate linear infinite;
  filter: blur(1px);
  z-index: -1;
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
}

@keyframes rotate {
  to {
    --angle: 360deg;
  }
}

@property --angle {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}
</style>
