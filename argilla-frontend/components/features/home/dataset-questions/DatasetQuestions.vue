<template>
  <BaseBadgeSkeleton v-if="isQuestionsLoading" :quantity="3" />
  <div class="questions" v-else>
    <span class="questions__title">{{ $t("questions") }}</span>
    <DatasetBadge
      v-for="question in questions"
      :key="question.id"
      :text="$t(question.type)"
      font-size="11px"
      color="hsl(220, 40%, 53%)"
    />
  </div>
</template>
<script>
import { useDatasetQuestions } from "./useDatasetQuestions";

export default {
  name: "DatasetQuestions",
  props: {
    dataset: {
      type: Object,
    },
  },
  setup(props) {
    return useDatasetQuestions(props);
  },
};
</script>

<style scoped lang="scss">
.questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  &__title {
    @include font-size(12px);
    color: var(--fg-tertiary);
    font-weight: 200;
  }
}
</style>
