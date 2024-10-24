<template>
  <div class="dataset-badge">
    <span v-if="icon" class="dataset-badge__icon-wrapper"
      ><svgicon :name="icon" :color="color" class="dataset-badge__icon"
    /></span>
    <span class="dataset-badge__text">{{ text }}</span>
  </div>
</template>

<script>
import "assets/icons/text-classification";
import "assets/icons/question-answering";
import "assets/icons/text-to-image";
export default {
  props: {
    text: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
    },
    color: {
      type: String,
    },
  },
};
</script>
<style lang="scss" scoped>
.dataset-badge {
  display: flex;
  align-items: center;
  min-height: 26px;
  box-shadow: 0 0 1px 1px var(--bg-opacity-10);
  border-radius: $border-radius;

  &__icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: calc($base-space / 1.5) $base-space;
    border-radius: $border-radius;
    background: linear-gradient(
      180deg,
      hsl(from v-bind(color) h s l / 1%) 0%,
      hsl(from v-bind(color) h s l / 10%) 100%
    );
  }
  &__icon {
    fill: v-bind(color);
    width: 16px;
    height: 16px;
  }
  &__text {
    font-weight: 400;
    color: var(--fg-secondary);
    padding: calc($base-space / 2) $base-space;
  }
}
</style>
