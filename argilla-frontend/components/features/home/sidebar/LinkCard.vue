<template>
  <BaseButton class="guide-link" target="_blank" :href="link">
    <div class="guide-link__content">
      <p class="guide-link__type">{{ type }}</p>
      <p class="guide-link__title">{{ text }}</p>
    </div>
  </BaseButton>
</template>

<script>
export default {
  props: {
    type: {
      type: String,
      required: true,
    },
    text: {
      type: String,
      required: true,
    },
    link: {
      type: String,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.guide-link {
  &.button {
    max-width: 75%;
    padding: $base-space * 2;
    border: 1px solid var(--bg-opacity-6);
    border-radius: $border-radius-m;
    background: var(--bg-accent-grey-2);
    color: var(--fg-primary);
    text-align: left;
    @include media("<desktop") {
      max-width: 100%;
    }
    &:hover {
      background: var(--bg-accent-grey-3);
      border: 1px solid var(--bg-opacity-10);
    }
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space * 2;
  }
  &__type {
    margin: 0;
    color: var(--fg-tertiary);
    @include font-size(12px);
  }
  &__title {
    margin: 0;
    color: var(--fg-primary);
  }
}
</style>
