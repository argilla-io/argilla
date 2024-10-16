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

    <template v-if="noMapping">
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
    <DatasetConfigurationColumnSelector
      class="config-card__type"
      :options="columns"
      v-model="question.column"
    />
    <BaseCheckbox
      class="config-card__required"
      :value="question.required"
      @input="question.required = !question.required"
    >
      Required question</BaseCheckbox
    >
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
    noMapping() {
      return this.question.column === "no mapping";
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
    position: absolute;
    top: $base-space * 1.5;
    right: $base-space * 1.5;
    padding: 0;
  }
  &__required {
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
}
</style>
