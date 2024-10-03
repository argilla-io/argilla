<template>
  <DatasetConfigurationCard :item="field" :type-options="typeOptions">
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
    typeOptions: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "type",
    event: "change",
  },
};
</script>
