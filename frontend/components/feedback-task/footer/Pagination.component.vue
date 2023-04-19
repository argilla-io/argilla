<template>
  <div class="pagination-component">
    <div class="number-of-records-by-page-area"></div>

    <div class="center-area">
      <button
        class="button"
        @click="onClickPrev"
        v-text="prevButtonMessage"
        :disabled="currentPage === 1"
      />

      <div class="page-number-area" v-if="showPageNumber">
        <button
          v-for="page in totalPages"
          :key="page"
          @click="onClickNumber(page)"
          :disabled="isCurrentPage(page)"
        >
          <span v-text="page" />
        </button>
      </div>

      <button
        @click="onClickNext"
        v-text="nextButtonMessage"
        :disabled="currentPage >= totalPages"
      />
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
      default: () => "Next >",
    },
    prevButtonMessage: {
      type: String,
      default: () => "< Prev",
    },
    showPageNumber: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      currentPage: 1,
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalItems / this.numberOfItemsByPage);
    },
    totalOfRecordMessage() {
      return `${this.currentPage} of ${this.totalItems} records`;
    },
  },
  watch: {
    currentPage: {
      immediate: true,
      handler(newCurrentPage) {
        this.emitCurrentPage();
        this.updateUrlParams(newCurrentPage);
      },
    },
  },
  mounted() {
    this.currentPage = parseFloat(this.$route.query?._page) || 1;
  },
  methods: {
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
      return +this.currentPage === +page;
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
.pagination-component {
  display: grid;
  grid-template-areas: "left center right";
  grid-template-columns: auto 1fr auto;
  grid-template-rows: 56px;
  background: #fafafa;
  border-top: 1px solid #e6e6e6;
}

.number-of-records-by-page-area {
  grid-area: right;
}
.center-area {
  grid-area: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

.total-records-area {
  grid-area: left;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
