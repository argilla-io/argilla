<template>
  <BaseBadgeSkeleton v-if="isQuestionsLoading" :quantity="3" />
  <div class="questions" v-else>
    <BaseBadge
      v-for="question in questions"
      :key="question.id"
      :text="$t(question.type)"
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

<style scoped>
.questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
