<template>
  <div class="pagination">
    <span class="pagination__info" v-if="!!items">
      {{ currentPaginationRange }} of {{ items }}</span
    >
    <div class="pagination__buttons">
      <BaseButton
        class="pagination__button"
        ref="prevButton"
        @click="onClickPrev"
        :disabled="isFirstPage"
        :title="
          $platform.isMac
            ? $t('shortcuts.pagination.go_to_previous_record_mac')
            : $t('shortcuts.pagination.go_to_previous_record')
        "
      >
        <svgicon name="chevron-left" width="12" height="12" />
      </BaseButton>

      <BaseButton
        class="pagination__button"
        ref="nextButton"
        @click="onClickNext"
        :title="
          $platform.isMac
            ? $t('shortcuts.pagination.go_to_next_record_mac')
            : $t('shortcuts.pagination.go_to_next_record')
        "
      >
        <svgicon name="chevron-right" width="12" height="12" />
      </BaseButton>
    </div>
  </div>
</template>

<script>
export default {
  name: "PaginationComponent",
  props: {
    currentPage: {
      type: Number,
      default: () => 1,
    },
    items: {
      type: Number,
      default: () => 0,
    },
    itemsPerPage: {
      type: Number,
      default: () => 1,
    },
  },
  computed: {
    isFirstPage() {
      return this.currentPage === 1;
    },
    totalPages() {
      return Math.ceil(this.items / this.itemsPerPage);
    },
    currentPaginationRange() {
      return this.itemsPerPage > 1
        ? `${this.currentRangeFrom} - ${this.currentRangeTo}`
        : this.currentPage;
    },
    currentRangeFrom() {
      return this.itemsPerPage * this.currentPage - (this.itemsPerPage - 1);
    },
    currentRangeTo() {
      return this.itemsPerPage * this.currentPage > this.items
        ? this.items
        : this.itemsPerPage * this.currentPage;
    },
  },
  mounted() {
    document.addEventListener("keydown", this.onPressKeyboardShortcuts);
  },
  destroyed() {
    document.removeEventListener("keydown", this.onPressKeyboardShortcuts);
  },
  methods: {
    stopPropagationForNativeBehavior(event) {
      event.preventDefault();
      event.stopPropagation();
    },
    onPressKeyboardShortcuts(event) {
      const { code, ctrlKey, metaKey } = event;
      if (this.$platform.isMac) {
        if (!metaKey) return;
      } else {
        if (!ctrlKey) return;
      }

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
        default:
        // Do nothing => the code is not registered as shortcut
      }
    },
    onClickPrev() {
      this.$emit("on-click-prev");
    },
    onClickNext() {
      this.$emit("on-click-next");
    },
  },
};
</script>

<style lang="scss" scoped>
.pagination {
  display: flex;
  gap: $base-space;
  justify-content: right;
  align-items: center;
  &__buttons {
    display: flex;
    gap: $base-space;
  }
  &__info {
    @include font-size(13px);
    color: $black-37;
  }
  &__button.button {
    justify-content: center;
    padding: $base-space;
    &:hover:not([disabled]) {
      background: $black-4;
    }
  }
}
</style>
