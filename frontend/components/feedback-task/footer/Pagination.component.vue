<template>
  <div class="pagination">
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
        <svgicon name="chevron-left" width="8" height="8" />
        {{ prevButtonMessage }}
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
        {{ nextButtonMessage }}
        <svgicon name="chevron-right" width="8" height="8" />
      </BaseButton>
    </div>
  </div>
</template>

<script>
import { usePaginationViewModel } from "./usePaginationViewModel";

export default {
  name: "PaginationComponent",
  props: {
    currentPage: {
      type: Number,
      default: () => 1,
    },
    nextButtonMessage: {
      type: String,
      default: () => "Next",
    },
    prevButtonMessage: {
      type: String,
      default: () => "Prev",
    },
  },
  computed: {
    pageFromRoute() {
      return parseFloat(this.$route.query?._page) || 1;
    },
  },
  emits: ["on-click-prev", "on-click-next"],
  setup(props, context) {
    return usePaginationViewModel(props, context);
  },
};
</script>

<style lang="scss" scoped>
.pagination {
  display: grid;
  grid-template-areas: "left center right";
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 56px;
  background: #fafafa;
  border-top: 1px solid $black-10;
  &__buttons {
    grid-area: center;
    display: flex;
    gap: $base-space;
    justify-content: center;
    align-items: center;
  }
  &__page-number-area {
    display: flex;
    gap: $base-space;
  }
  &__button {
    min-width: 30px;
    min-height: 30px;
    justify-content: center;
    padding: 0 10px;
    .pagination__page-number-area & {
      padding: 5px;
    }
    &:hover:not([disabled]) {
      background: $black-4;
    }
  }
}

.number-of-records-by-page-area {
  grid-area: right;
  padding-right: $base-space * 7;
}

.total-records-area {
  grid-area: left;
  display: flex;
  align-items: center;
  padding-left: $base-space * 7;
}
</style>
