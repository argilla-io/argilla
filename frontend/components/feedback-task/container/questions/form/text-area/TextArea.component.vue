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
    isSuggested() {
      return this.question.suggestion?.isSuggested(this.question.answer.value);
    },
    getScore() {
      return this.question.suggestion?.score;
    },
    getAgent() {
      return this.question.suggestion?.agent;
    },
    tabs() {
      return [
        {
          id: "0",
          name: this.isSuggested ? "Suggestion" : "Write",
          icon: this.isSuggested && "suggestion",
          info: this.isSuggested && this.getScore,
          tooltipTitle: this.isSuggested && this.$nuxt.$t("suggestion.name"),
          tooltipText: this.isSuggested && this.getAgent,
          component: "TextAreaContents",
        },
        ...(!this.isSuggested
          ? [
              {
                id: "1",
                name: "Suggestion",
                icon: "suggestion",
                info: this.getScore,
                tooltipTitle: this.$nuxt.$t("suggestion.name"),
                tooltipText: this.getAgent,
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
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}
</style>
