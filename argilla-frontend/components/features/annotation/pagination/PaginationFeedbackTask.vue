<template>
  <div class="pagination" v-if="records.hasRecordsToAnnotate">
    <PageSizeSelector
      v-if="isBulkMode"
      :options="recordCriteria.page.options"
      v-model="recordCriteria.page.client.many"
    />
    <span class="pagination__info">
      <span aria-label="Current Record">{{ currentPage }}</span>
      <span class="pagination__info--bulk" v-if="isBulkMode">
        -
        {{ currentPageEnd }}</span
      >
      <span aria-label="Total Records">of {{ records.total }}</span>
    </span>
    <Pagination :recordCriteria="recordCriteria" :total="records.total" />
  </div>
</template>

<script>
import { usePaginationFeedbackTaskViewModel } from "./usePaginationFeedbackTaskViewModel";

export default {
  name: "PaginationFeedbackTask",
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  computed: {
    isBulkMode() {
      return this.recordCriteria.committed.page.isBulkMode;
    },
    currentPage() {
      return this.recordCriteria.committed.page.client.page;
    },
    currentPageEnd() {
      return this.currentPage + this.currentPageItemsSize - 1 >
        this.records.total
        ? this.records.total
        : this.currentPage + this.currentPageItemsSize - 1;
    },
    currentPageItemsSize() {
      return this.recordCriteria.committed.page.client.many;
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
    gap: calc($base-space/2);
    display: flex;
    align-items: center;
    flex-direction: row;
    color: var(--fg-tertiary);

    &--bulk {
      align-items: center;
      display: flex;
      gap: calc($base-space/2);
    }
  }
}
</style>
