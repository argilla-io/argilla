<template>
  <DatasetConfigurationCard
    :item="question"
    :available-types="availableTypes"
    @is-focused="$emit('is-focused', $event)"
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
    <DatasetConfigurationLabels
      v-if="
        question.settings.type.isSingleLabelType ||
        question.settings.type.isMultiLabelType ||
        question.settings.type.isSpanType
      "
      v-model="question.settings.options"
      @is-focused="$emit('is-focused', $event)"
    />
    <DatasetConfigurationRating
      v-else-if="question.settings.type.isRatingType"
      v-model="question.settings.options"
      @is-focused="$emit('is-focused', $event)"
    />
    <DatasetConfigurationRanking
      v-else-if="question.settings.type.isRankingType"
      v-model="question.settings.options"
      @is-focused="$emit('is-focused', $event)"
    />
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
    availableTypes: {
      type: Array,
      required: true,
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
