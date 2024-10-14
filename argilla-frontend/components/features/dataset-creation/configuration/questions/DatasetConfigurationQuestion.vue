<template>
  <DatasetConfigurationCard
    :item="question"
    :available-types="availableTypes"
    @is-focused="$emit('is-focused', $event)"
    @change-type="$emit('change-type', $event)"
  >
    <BaseButton
      class="config-card__remove"
      @click="remove"
      v-if="removeIsAllowed"
      ><svgicon name="close"
    /></BaseButton>

    <DatasetConfigurationSelector
      class="config-card__type"
      :options="columns"
      v-model="question.column"
    />
    <!-- <BaseSwitch
      v-if="question.settings.type.isTextType"
      class="config-card__remove__switch"
      v-model="question.use_markdown"
      >{{ $t("useMarkdown") }}</BaseSwitch
    > -->
    <DatasetConfigurationLabels
      v-if="
        question.settings.type.isSingleLabelType ||
        question.settings.type.isMultiLabelType
      "
      v-model="question.settings.options"
      @is-focused="$emit('is-focused', $event)"
    />
    <DatasetConfigurationSpan
      v-else-if="question.settings.type.isSpanType"
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
import "assets/icons/close";
export default {
  props: {
    question: {
      type: Object,
      required: true,
    },
    columns: {
      type: Array,
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
    position: absolute;
    top: $base-space * 1.5;
    right: $base-space * 1.5;
    padding: 0;
  }
}
</style>
