<template>
  <DatasetConfigurationCard
    :item="field"
    config-type="field"
    :available-types="availableTypes"
    @is-focused="$emit('is-focused', $event)"
  >
    <BaseCheckbox
      class="config-card__required"
      v-if="!hasNoMapping"
      :value="field.required"
      @input="field.required = !field.required"
    >
      {{ $t("datasetCreation.requiredField") }}</BaseCheckbox
    >
  </DatasetConfigurationCard>
</template>

<script>
export default {
  props: {
    field: {
      type: Object,
      required: true,
    },
    availableTypes: {
      type: Array,
      required: true,
    },
  },
  computed: {
    hasNoMapping() {
      return this.field.type.value === "no mapping";
    },
  },
  model: {
    prop: "type",
    event: "change",
  },
};
</script>

<style lang="scss" scoped>
.config-card__required {
  display: flex;
  gap: $base-space;
  margin-top: $base-space;
  @include font-size(12px);
  flex-flow: row-reverse;
  justify-content: flex-end;
  &:deep(.checkbox__container) {
    margin: 0;
    border-color: var(--bg-opacity-20);
    background: var(--bg-accent-grey-1);
  }
}
</style>
