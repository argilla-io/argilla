<template>
  <BaseButton
    class="example-dataset"
    @click="$emit('on-import-dataset', dataset.repoId)"
  >
    <div class="example-dataset__content">
      <p class="example-dataset__title">{{ dataset.repoId }}</p>
      <div class="example-dataset__tags">
        <DatasetBadge
          :text="dataset.task"
          :icon="dataset.icon"
          :color="dataset.color"
        />
        <DatasetBadge v-for="tag in dataset.tags" :text="tag" :key="tag" />
      </div>
    </div>
  </BaseButton>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.example-dataset {
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
  &__title {
    margin: 0;
    color: var(--fg-primary);
  }
  &__tags {
    display: flex;
    gap: $base-space;
    flex-wrap: wrap;
  }
}
</style>
