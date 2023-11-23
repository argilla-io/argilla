<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />
    <TextAreaContents
      v-if="!question.suggestion"
      :question="question"
      :is-focused="isFocused"
    />
    <BaseCardWithTabs v-else :tabs="tabs">
      <template v-slot="{ currentComponent }">
        <component
          :question="question"
          :is-focused="isFocused"
          :is="currentComponent"
          :key="currentComponent"
        />
      </template>
    </BaseCardWithTabs>
  </div>
</template>

<script>
export default {
  name: "TextAreaComponent",
  props: {
    question: {
      type: Object,
      required: true,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  computed: {
    tabs() {
      return [
        {
          id: "0",
          name: this.question.matchSuggestion ? "Suggestion" : "Write",
          class: this.question.matchSuggestion ? "--suggestion" : null,
          component: "TextAreaContents",
        },
        ...(this.question.suggestion && !this.question.matchSuggestion
          ? [
              {
                id: "1",
                name: "Suggestion",
                class: "--suggestion",
                component: "TextAreaSuggestion",
              },
            ]
          : []),
      ];
    },
  },
};
</script>

<style lang="scss" scoped>
$suggestion-color: palette(yellow, 400);
$suggestion-color-darken: darken($suggestion-color, 24%);
$suggestion-color-lighten: lighten($suggestion-color, 24%);

.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}
.--suggestion {
  :deep(.card-with-tabs__content) {
    border-color: $suggestion-color-darken;
    background: $suggestion-color-lighten;
  }
}
:deep(.card-with-tabs__tab.--suggestion) {
  border-top-color: $suggestion-color-darken;
  border-left-color: $suggestion-color-darken;
  border-right-color: $suggestion-color-darken;
  border-bottom-color: $suggestion-color-lighten;
  background: $suggestion-color-lighten;
}
</style>
