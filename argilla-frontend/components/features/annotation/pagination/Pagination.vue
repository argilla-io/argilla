<template>
  <div class="pagination__buttons">
    <BaseButton
      ref="prevButton"
      class="pagination__button"
      :disabled="isFirstPage"
      :data-title="$t('shortcuts.pagination.go_to_previous_record')"
      @click="goToPrevPage"
    >
      <svgicon name="chevron-left" width="12" height="12" />
    </BaseButton>

    <BaseButton
      ref="nextButton"
      class="pagination__button"
      :disabled="isLastPage"
      :data-title="$t('shortcuts.pagination.go_to_next_record')"
      @click="goToNextPage"
    >
      <svgicon name="chevron-right" width="12" height="12" />
    </BaseButton>
  </div>
</template>

<script>
export default {
  name: "Pagination",
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
    total: {
      type: Number,
      required: true,
    },
  },
  mounted() {
    document.addEventListener("keydown", this.onPressKeyboardShortcuts);
  },
  destroyed() {
    document.removeEventListener("keydown", this.onPressKeyboardShortcuts);
  },
  computed: {
    currentPage() {
      return this.recordCriteria.committed.page.client.page;
    },
    currentPageSize() {
      return this.recordCriteria.committed.page.client.many;
    },
    isFirstPage() {
      return this.recordCriteria.page.isFirstPage();
    },
    isLastPage() {
      if (this.isBulkMode) {
        return this.currentPage + this.currentPageSize >= this.total;
      } else {
        return this.currentPage === this.total;
      }
    },
    isBulkMode() {
      return this.recordCriteria.committed.page.isBulkMode;
    },
  },
  methods: {
    stopPropagationForNativeBehavior(event) {
      event.preventDefault();
      event.stopPropagation();
    },
    onPressKeyboardShortcuts(event) {
      const { code, ctrlKey, metaKey, shiftKey } = event;

      if (ctrlKey || metaKey || shiftKey) return;

      switch (code) {
        case "ArrowRight": {
          this.stopPropagationForNativeBehavior(event);
          const elem = this.$refs.nextButton.$el;
          elem.click();
          break;
        }
        case "ArrowLeft": {
          this.stopPropagationForNativeBehavior(event);
          const elem = this.$refs.prevButton.$el;
          elem.click();
          break;
        }
      }
    },
    goToNextPage() {
      this.recordCriteria.nextPage();

      this.$root.$emit("on-change-record-page", this.recordCriteria);
    },
    goToPrevPage() {
      this.recordCriteria.previousPage();

      this.$root.$emit("on-change-record-page", this.recordCriteria);
    },
  },
};
</script>

<style lang="scss" scoped>
.pagination {
  &__buttons {
    display: flex;
  }
  &__button.button {
    justify-content: center;
    padding: $base-space;
    &:hover:not([disabled]) {
      background: var(--bg-opacity-4);
    }
  }
}
.button[data-title] {
  overflow: visible;
  @include tooltip-mini("top");
}
</style>
