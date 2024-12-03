<template>
  <BaseBadgeSkeleton font-size="11px" v-if="isQuestionsLoading" :quantity="3" />
  <div class="questions" v-else>
    <div class="questions__badges">
      <BaseBadge
        v-for="question in questions"
        :key="question.id"
        :text="$t(question.type)"
        font-size="11px"
        color="var(--fg-label)"
      />
    </div>
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
  gap: calc($base-space / 2);
  &__badges {
    display: flex;
    flex-wrap: wrap;
    gap: calc($base-space / 2);
  }
}
</style>
