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
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}
.--suggestion {
  :deep(.card-with-tabs__content) {
    border-color: $suggestion-color;
    background: lighten($suggestion-color, 24%);
  }

  :deep(.card-with-tabs__tab.--active) {
    border-top-color: $suggestion-color;
    border-left-color: $suggestion-color;
    border-right-color: $suggestion-color;
    border-bottom-color: lighten($suggestion-color, 24%);
    background: lighten($suggestion-color, 24%);
  }
}
</style>
