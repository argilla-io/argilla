<template>
  <div class="pagination">
    <div class="number-of-records-by-page-area"></div>

    <div class="pagination__buttons">
      <BaseButton
        class="pagination__button"
        ref="prevButton"
        @click="onPaginate(onClickPrev)"
        :disabled="currentPage === 1"
      >
        <svgicon name="chevron-left" width="8" height="8" />
        {{ prevButtonMessage }}
      </BaseButton>

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
        ref="nextButton"
        @click="onPaginate(onClickNext)"
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
import { Notification } from "@/models/Notifications";

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
    notificationParams: {
      type: Object | null,
    },
    conditionToShowNotificationComponentOnPagination: {
      type: Function | null,
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
    onBusEventCurrentPage() {
      this.$root.$on("current-page", (currentPage) => {
        this.currentPage = currentPage;
      });
    },
    onPaginate(eventToFire) {
      if (this.isNotificationComponentForThisPage()) {
        const { message, buttonMessage, typeOfToast } = this.notificationParams;
        this.showNotificationBeforePaginate({
          eventToFire,
          message,
          buttonMessage,
          typeOfToast,
        });
      } else {
        eventToFire();
      }
    },
    isNotificationComponentForThisPage() {
      if (
        this.notificationParams &&
        this.conditionToShowNotificationComponentOnPagination
      ) {
        const showNotification =
          this.conditionToShowNotificationComponentOnPagination(
            this.currentPage
          );

        return showNotification;
      }
      return false;
    },
    showNotificationBeforePaginate({
      eventToFire,
      message,
      buttonMessage,
      typeOfToast,
    }) {
      Notification.dispatch("notify", {
        message: message ?? "",
        numberOfChars: 20000,
        type: typeOfToast ?? "warning",
        buttonText: buttonMessage ?? "",
        async onClick() {
          eventToFire();
        },
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
