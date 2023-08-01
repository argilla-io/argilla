<template>
  <div class="title-area --body1">
    <span
      class="suggestion-info"
      v-text="question.title"
      v-optional-field="!question.isRequired"
      v-prefix-star="{
        show: showPrefixStar,
        tooltip: 'This question contains a suggestion',
      }"
    />
    <BaseIconWithBadge
      class="icon-info"
      v-if="showIcon"
      icon="info"
      :id="`${question.title}QuestionHeader`"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
      v-tooltip="{ content: question.description, backgroundColor: '#FFF' }"
    />
  </div>
</template>

<script>
import "assets/icons/info";
export default {
  name: "QuestionHeader",
  props: {
    question: {
      type: Object,
      required: true,
    },
    showSuggestion: {
      type: Boolean,
      default: () => false,
    },
  },
  data() {
    return {
      showPrefixStar: this.showSuggestion && this.question.matchSuggestion,
    };
  },
  computed: {
    showIcon() {
      return !!this.question.description?.length;
    },
  },
  watch: {
    "question.matchSuggestion"() {
      this.showPrefixStar =
        this.showSuggestion && this.question.matchSuggestion;
    },
  },
};
</script>

<style lang="scss" scoped>
.title-area {
  color: $black-87;
  font-weight: 500;
}

.icon {
  color: $black-37;
}

.info-icon {
  display: flex;
  flex-basis: 37px;
}

span {
  word-break: break-word;
  line-height: 1.2em;
}

.icon-info {
  display: inline-flex;
  width: 20px;
  height: 20px;
  margin: 0;
  padding: 0;
  overflow: inherit;
  vertical-align: middle;
  &[data-title] {
    position: relative;
    overflow: visible;
    &:before,
    &:after {
      margin-top: 0;
    }
  }
}
:deep([data-title]):hover {
  position: relative;
  cursor: pointer;
  @extend %has-tooltip--top;
  &:after {
    transform: none;
    right: auto;
    left: -1.5em;
  }
}
</style>
