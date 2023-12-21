<template>
  <div class="pagination" v-if="records.hasRecordsToAnnotate">
    <span class="pagination__info">
      <span>{{ currentPage }}</span>
      <span
        class="pagination__info--bulk"
        v-if="recordCriteria.committed.page.isBulkMode"
      >
        -
        <PageSizeSelector
          :options="recordCriteria.page.options"
          v-model="recordCriteria.page.client.many"
        />
      </span>
      <span>of {{ records.total }}</span>
    </span>
    <PaginationComponent
      :recordCriteria="recordCriteria"
      :total="records.total"
    />
  </div>
</template>

<script>
import { usePaginationFeedbackTaskViewModel } from "./usePaginationFeedbackTaskViewModel";

export default {
  name: "PaginationFeedbackTaskComponent",
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  computed: {
    currentPage() {
      return this.recordCriteria.committed.page.client.page;
    },
  },
  setup() {
    return usePaginationFeedbackTaskViewModel();
  },
};
</script>

<style lang="scss" scoped>
.pagination {
  user-select: none;
  display: flex;
  gap: $base-space;
  justify-content: right;
  align-items: center;
  &__info {
    @include font-size(13px);
    gap: $base-space / 2;
    display: flex;
    align-items: center;
    flex-direction: row;
    color: $black-37;

    &--bulk {
      align-items: center;
      display: flex;
      gap: $base-space / 2;
    }
  }
}
</style>
