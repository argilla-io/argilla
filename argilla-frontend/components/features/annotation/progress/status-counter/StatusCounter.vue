<template>
  <li class="status-counter">
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
</style>
