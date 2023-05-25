<template>
  <div class="pagination">
    <div class="pagination__buttons">
      <BaseButton
        class="pagination__button"
        ref="prevButton"
        @click="onClickPrev"
        :disabled="isFirstPage"
      >
        <svgicon name="chevron-left" width="8" height="8" />
        {{ prevButtonMessage }}
      </BaseButton>

      <BaseButton
        class="pagination__button"
        ref="nextButton"
        @click="onClickNext"
        :disabled="false"
      >
        {{ nextButtonMessage }}
        <svgicon name="chevron-right" width="8" height="8" />
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
    isFirstPage() {
      return this.currentPage === 1;
    },
    // TODO: Move to the parent
    pageFromRoute() {
      return parseFloat(this.$route.query?._page) || 1;
    },
  },
  mounted() {
    document.addEventListener("keydown", this.onPressKeyboardShortCut);
  },
  destroyed() {
    // TODO: Move this to the parent
    document.removeEventListener("keydown", this.onPressKeyboardShortCut);
  },
  methods: {
    onPressKeyboardShortCut({ code }) {
      switch (code) {
        case "ArrowRight": {
          const elem = this.$refs.nextButton.$el;
          elem.click();
          break;
        }
        case "ArrowLeft": {
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
