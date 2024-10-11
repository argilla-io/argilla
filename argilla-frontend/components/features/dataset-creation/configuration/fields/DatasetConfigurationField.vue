<template>
  <DatasetConfigurationCard
    :item="field"
    :available-types="availableFieldTypes"
    @is-focused="$emit('is-focused', $event)"
  >
    <!-- <BaseSwitch
      v-if="field.type.isTextType || field.type.isChatType"
      class="config-card__remove__switch"
      v-model="field.use_markdown"
      >{{ $t("useMarkdown") }}</BaseSwitch
    > -->
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
