<template>
  <div class="pagination">
    <div class="number-of-records-by-page-area"></div>

    <div class="pagination__buttons">
      <BaseButton
        class="pagination__button"
        @click="onClickPrev"
        :disabled="currentPage === 1"
        ><svgicon name="chevron-left" width="8" height="8" />{{
          prevButtonMessage
        }}</BaseButton
      >

      <div class="pagination__page-number-area" v-if="showPageNumber">
        <BaseButton
          v-for="page in totalPages"
          :key="page"
          class="pagination__button"
          @click="onClickNumber(page)"
          :disabled="isCurrentPage(page)"
        >
          {{ page }}
        </BaseButton>
      </div>

      <BaseButton
        class="pagination__button"
        @click="onClickNext"
        :disabled="currentPage >= totalPages"
      >
        {{ nextButtonMessage }}
        <svgicon name="chevron-right" width="8" height="8" />
      </BaseButton>
    </div>

    <div class="total-records-area">
      <span v-text="totalOfRecordMessage" />
    </div>
  </div>
</template>

<script>
export default {
  name: "PaginationComponent",
  props: {
    totalItems: {
      type: Number,
      required: true,
    },
    numberOfItemsByPage: {
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
    showPageNumber: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      localCurrentPage: 1,
    };
  },
  computed: {
    currentPage: {
      get() {
        return this.localCurrentPage;
      },
      set(newCurrentPage) {
        this.localCurrentPage = +newCurrentPage;
      },
    },
    totalPages() {
      return Math.ceil(this.totalItems / this.numberOfItemsByPage);
    },
    totalOfRecordMessage() {
      return `${this.currentPage} of ${this.totalItems} records`;
    },
  },
  watch: {
    localCurrentPage: {
      immediate: true,
      handler(newCurrentPage) {
        this.emitCurrentPage();
        this.updateUrlParams(newCurrentPage);
      },
    },
  },
  mounted() {
    this.currentPage = parseFloat(this.$route.query?._page) || 1;

    document.addEventListener("keydown", this.onPressKeyboardShortCut);

    this.onBusEventCurrentPage();
  },
  destroyed() {
    document.removeEventListener("keydown", this.onPressKeyboardShortCut);
    this.$root.$off("current-page");
  },
  methods: {
    onPressKeyboardShortCut({ code }) {
      switch (code) {
        case "ArrowRight": {
          this.onClickNext();
          break;
        }
        case "ArrowLeft": {
          this.onClickPrev();
          break;
        }
        default:
      }
    },
    onBusEventCurrentPage() {
      this.$root.$on("current-page", (currentPage) => {
        this.currentPage = currentPage;
      });
    },
    onClickPrev() {
      this.currentPage > 1 && this.currentPage--;
    },
    onClickNext() {
      this.currentPage < this.totalPages && this.currentPage++;
    },
    onClickNumber(pageValue) {
      this.currentPage = pageValue;
    },
    emitCurrentPage() {
      this.$emit("on-paginate", this.currentPage);
    },
    isCurrentPage(page) {
      return this.currentPage === page;
    },
    updateUrlParams(currentPage) {
      this.$router.push({
        path: this.$route.path,
        query: { _page: currentPage },
      });
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
