<template>
  <DatasetConfigurationCard :item="field" :type-options="typeOptions">
    <template slot="header">
      <BaseButton
        class="config-card__remove"
        @click="remove"
        v-if="removeIsAllowed"
        >Remove</BaseButton
      >
    </template>
    <BaseSwitch
      v-if="field.isTextType || field.isChatType"
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
    removeIsAllowed: {
      type: Boolean,
      default: false,
    },
  },
  model: {
    prop: "type",
    event: "change",
  },
  methods: {
    remove() {
      this.$emit("remove");
    },
  },
};
</script>
