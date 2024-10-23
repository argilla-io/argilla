<template>
  <BaseButton class="guide-link" target="_blank" :href="link">
    <div class="guide-link__content">
      <BaseBadge :text="badge" class="guide-link__badge" />
      <p class="guide-link__title">{{ text }}</p>
    </div>
  </BaseButton>
</template>

<script>
export default {
  props: {
    badge: {
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
    width: 100%;
    padding: $base-space * 2;
    border: 1px solid var(--bg-opacity-6);
    border-radius: $border-radius-m;
    background: var(--bg-accent-grey-2);
    color: var(--fg-primary);
    text-align: left;
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
  &__badge {
    background: hsl(from hsl(235, 24%, 60%) h s l / 20%);
    border-color: hsl(from hsl(235, 24%, 60%) h s l / 30%);
  }
  &__title {
    margin: 0;
    color: var(--fg-primary);
  }
}
</style>
