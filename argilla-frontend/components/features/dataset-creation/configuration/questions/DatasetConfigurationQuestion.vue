<template>
  <DatasetConfigurationCard
    :item="question"
    :type-options="question.availableTypes"
  >
    <template slot="header">
      <BaseButton
        class="config-card__remove"
        @click="remove"
        v-if="removeIsAllowed"
        ><svgicon name="close"
      /></BaseButton>
    </template>
    <BaseSwitch
      v-if="question.settings.type.isTextType"
      class="config-card__remove__switch"
      v-model="question.use_markdown"
      >{{ $t("useMarkdown") }}</BaseSwitch
    >
  </DatasetConfigurationCard>
</template>

<script>
export default {
  props: {
    question: {
      type: Object,
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

<style lang="scss" scoped>
.config-card {
  &__remove.button {
    padding: 0;
  }
}
</style>
