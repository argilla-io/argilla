<template>
  <DatasetConfigurationCard
    :item="field"
    :available-types="[...availableFieldTypes, ...availableMetadataTypes]"
    @is-focused="$emit('is-focused', $event)"
  >
    <BaseSwitch
      v-if="field.type.isTextType || field.type.isChatType"
      class="config-card__remove__switch"
      v-model="field.use_markdown"
      >{{ $t("useMarkdown") }}</BaseSwitch
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
    availableFieldTypes: {
      type: Array,
      required: true,
    },
    availableMetadataTypes: {
      type: Array,
      required: true,
    },
  },
  watch: {
    field: {
      handler() {
        if (this.availableMetadataTypes.includes(this.field.type)) {
          this.$emit("metadata-type-selected", this.field);
        }
      },
      deep: true,
    },
  },
  model: {
    prop: "type",
    event: "change",
  },
};
</script>
