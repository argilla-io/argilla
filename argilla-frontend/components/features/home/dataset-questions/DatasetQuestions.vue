<template>
  <BaseBadgeSkeleton font-size="11px" v-if="isQuestionsLoading" :quantity="3" />
  <div class="questions" v-else>
    <span class="questions__title">{{ $t("questions") }}</span>
    <div class="questions__badges">
      <BaseBadge
        v-for="question in questions"
        :key="question.id"
        :text="$t(question.type)"
        font-size="11px"
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
  gap: $base-space;
  &__title {
    @include font-size(12px);
    color: var(--fg-secondary);
    min-width: $base-space * 8;
  }
  &__badges {
    display: flex;
    flex-wrap: wrap;
    gap: $base-space;
  }
}
</style>
