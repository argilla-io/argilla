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
    suggestedScore() {
      return this.question.suggestion?.score?.toFixed(1);
    },
    suggestedAgent() {
      return this.question.suggestion?.agent;
    },
    tabs() {
      return [
        {
          id: "0",
          name: this.isSuggested ? "" : this.$nuxt.$t("questions_form.write"),
          icon: this.isSuggested ? "suggestion" : "",
          info: this.isSuggested ? this.suggestedScore : "",
          tooltipTitle: this.isSuggested
            ? this.$nuxt.$t("suggestion.name")
            : "",
          tooltipText: this.isSuggested ? this.suggestedAgent : "",
          component: "TextAreaContents",
          label: this.isSuggested ? this.$nuxt.$t("suggestion.name") : this.$nuxt.$t("questions_form.write")
        },
        ...(!this.isSuggested
          ? [
              {
                id: "1",
                name: "",
                icon: "suggestion",
                info: this.suggestedScore,
                tooltipTitle: this.$nuxt.$t("suggestion.name"),
                tooltipText: this.suggestedAgent,
                component: "TextAreaSuggestion",
                label: this.$nuxt.$t("suggestion.name"),
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
  gap: $base-space * 1.5;
}
</style>
