<template>
  <DatasetConfigurationCard
    :item="question"
    :available-types="availableTypes"
    @is-focused="$emit('is-focused', $event)"
    @change-type="$emit('change-type', $event)"
  >
    <template slot="header">
      <BaseButton
        class="config-card__remove"
        @click="remove"
        v-if="removeIsAllowed"
        ><svgicon name="close"
      /></BaseButton>
    </template>
    <template slot="required">
      <BaseCheckbox
        :value="question.required"
        @input="question.required = !question.required"
        class="config-card__required"
      />
    </template>
    <DatasetConfigurationSelector
      class="config-card__type"
      :options="columns"
      v-model="question.datasetColumn"
    />
    <BaseSwitch
      v-if="question.settings.type.isTextType"
      class="config-card__remove__switch"
      v-model="question.use_markdown"
      >{{ $t("useMarkdown") }}</BaseSwitch
    >
    <template v-if="hasNoMapping">
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
    </template>
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
  computed: {
    hasNoMapping() {
      return this.question.datasetColumn === "no mapping";
    },
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
