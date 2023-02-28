<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <div class="pagination__container">
    <template v-if="!onePage">
      <div v-click-outside="closePageSizeSelector" class="pagination__selector">
        <span class="pagination__selector__title">Records per page:</span>
        <div class="pagination__selector__content">
          <a href="#" @click.prevent="showOptions = !showOptions">
            {{ paginationSize }}
            <svgicon name="chevron-up" width="12" height="12" />
          </a>
          <ul v-if="showOptions">
            <li v-for="item in availableItemsPerPage" :key="item">
              <a href="#" @click.prevent="changePageSize(item)">{{ item }}</a>
            </li>
          </ul>
        </div>
      </div>
      <div v-if="totalItems > paginationSize" class="pagination">
        <a
          href="#"
          class="pagination__arrow pagination__arrow--prev"
          :class="currentPage <= 1 ? 'is-disabled' : null"
          @click.prevent="prevPage"
        >
          <svgicon name="chevron-left" width="8" height="8" /> Prev
        </a>
        <ul class="pagination__numbers">
          <li v-if="totalPages > 1 && !pages.includes(1)">
            <a
              href="#"
              class="pagination__number"
              :class="currentPage === 1 ? 'is-current' : null"
              @click.prevent="changePage(1)"
            >
              {{ 1 }}
            </a>
          </li>
          <li v-if="pages.length && totalPages > 1 && !pages.includes(1 + 1)">
            ...
          </li>
          <template v-if="totalPages > 1">
            <li v-for="i in pages" :key="i">
              <a
                href="#"
                class="pagination__number"
                :class="currentPage === i ? 'is-current' : null"
                @click.prevent="changePage(i)"
              >
                {{ i }}
              </a>
            </li>
          </template>
          <li v-if="pages.length && !pages.includes(totalPages - 1)">...</li>
          <li v-if="!pages.includes(totalPages)">
            <a
              href="#"
              class="pagination__number"
              :class="currentPage === totalPages ? 'is-current' : null"
              @click.prevent="changePage(totalPages)"
            >
              {{ totalPages }}
            </a>
          </li>
        </ul>
        <a
          href="#"
          class="pagination__arrow pagination__arrow--next"
          :class="currentPage >= totalPages ? 'is-disabled' : null"
          @click.prevent="nextPage"
        >
          Next <svgicon name="chevron-right" width="8" height="8" />
        </a>
      </div>
    </template>
    <div class="pagination__info">
      <template v-if="!onePage">
        <strong>
          {{ paginationSize * currentPage - (paginationSize - 1) }}-{{
            paginationSize * currentPage > totalItems
              ? totalItems
              : paginationSize * currentPage
          }}
        </strong>
        of
      </template>
      <span class="total-records">{{ totalItems | formatNumber }} </span>
      records
    </div>
  </div>
</template>

<script>
import { Notification } from "@/models/Notifications";
import "assets/icons/chevron-left";
import "assets/icons/chevron-right";
import "assets/icons/chevron-up";
export default {
  props: {
    totalItems: {
      type: Number,
      required: true,
    },
    paginationSettings: {
      type: Object,
      required: true,
    },
    onePage: {
      type: Boolean,
      default: false,
    },
    visiblePagesRange: {
      type: Number,
      default: 5,
      validator: function (value) {
        return value > 1 && !(value % 2 == 0);
      },
    },
  },
  data() {
    return {
      showOptions: false,
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.paginableTotalItems / this.paginationSettings.size);
    },
    paginableTotalItems() {
      return this.totalItems >= this.maxRecordsLimit
        ? this.maxRecordsLimit
        : this.totalItems;
    },
    paginationSize() {
      return this.paginationSettings.size;
    },
    maxRecordsLimit() {
      return this.paginationSettings.maxRecordsLimit;
    },
    availableItemsPerPage() {
      return this.paginationSettings.pageSizeOptions.filter(
        (p) => p !== this.paginationSize
      );
    },
    currentPage() {
      return this.paginationSettings.page;
    },
    pages() {
      const rangeOfPages = (this.visiblePagesRange - 1) / 2;
      let start = this.currentPage - rangeOfPages;
      start = start > 0 ? start : 1;
      let end = this.currentPage + rangeOfPages;
      end = end < this.totalPages ? end : this.totalPages;
      var pages = [];
      for (var i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    },
    formattedLimit() {
      return this.$options.filters.formatNumber(this.maxRecordsLimit);
    },
    message() {
      return `<p>
                You cannot go through more than ${this.formattedLimit} records.
                To explore more records, you can combine queries, filters, and sorting to reduce your search results.
                Visit this
                <a
                  href="https://docs.argilla.io/en/latest/guides/features/queries.html?highlight=queries#"
                  target="_blank"
                >
                  guide</a
                > for using advanced queries.
              </p>`;
    },
  },
  watch: {
    currentPage(newValue) {
      this.isLastPageEqualToLimitSimilaritySearch(newValue) &&
        this.showNotification();
    },
  },
  mounted() {
    window.addEventListener("keydown", this.keyDown);
    this.isLastPageEqualToLimitSimilaritySearch(this.currentPage) &&
      this.showNotification();
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
  },
  methods: {
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.$emit("changePage", this.currentPage + 1, this.paginationSize);
      }
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.$emit("changePage", this.currentPage - 1, this.paginationSize);
      }
    },
    changePage(pageNumber) {
      this.$emit("changePage", pageNumber, this.paginationSize);
    },
    changePageSize(pageSize) {
      (this.showOptions = false),
        this.$emit(
          "changePage",
          this.paginationSize === pageSize ? this.currentPage : 1,
          pageSize
        );
    },
    closePageSizeSelector() {
      this.showOptions = false;
    },
    keyDown(event) {
      const arrowRight = event.keyCode === 39;
      const arrowLeft = event.keyCode === 37;
      const allowPagination =
        !this.paginationSettings.disabledShortCutPagination &&
        !this.isEditableAreaFocused(event);
      if (allowPagination) {
        if (arrowRight) {
          this.nextPage();
        } else if (arrowLeft) {
          this.prevPage();
        }
      }
    },
    isEditableAreaFocused(event) {
      return (
        event.target.tagName?.toLowerCase() === "input" ||
        event.target.contentEditable?.toLowerCase() === "true"
      );
    },
    showNotification() {
      Notification.dispatch("notify", {
        message: this.message,
        numberOfChars: 194,
        type: "warning",
      });
    },
    isLastPageEqualToLimitSimilaritySearch(pageNumber) {
      return pageNumber === this.maxRecordsLimit / this.paginationSize;
    },
  },
};
</script>
<style lang="scss" scoped>
$pagination-size: 30px;
.pagination {
  $self: &;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: auto;
  font-weight: 400;
  &__container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: $sidebarMenuWidth;
    display: flex;
    align-items: center;
    background: palette(grey, 800);
    border-top: 1px solid palette(grey, 600);
    min-height: 63px;
    z-index: 99;
    padding-right: 56px;
    padding-left: 4em;
    .--metrics & {
      @include media(">desktop") {
        padding-right: calc(294px + 10px);
        transition: padding 0.1s ease-in-out;
      }
    }
  }
  &__arrow {
    transition: all 0.3s ease-in-out;
    background: transparent;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    height: $pagination-size;
    padding: 0 10px;
    transition: color 200ms ease-in-out;
    outline: none;
    border-radius: $border-radius;
    svg {
      margin-top: 1px;
    }
    &:hover {
      transition: all 0.3s ease-in-out;
      background: $black-4;
    }
    &--next {
      margin-left: 1em;
      svg {
        margin-left: 0.5em;
      }
    }
    &--prev {
      margin-right: 1em;
      svg {
        margin-right: 0.5em;
      }
    }
    &.is-disabled {
      pointer-events: none;
      opacity: 0.5;
    }
  }
  &__numbers {
    display: flex;
    align-items: center;
    list-style: none;
    padding-left: 0;
    @include font-size(14px);
    #{$self}__number {
      transition: all 0.3s ease-in-out;
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      min-width: $pagination-size;
      height: $pagination-size;
      border-radius: $border-radius;
      margin: auto 0.5em;
      outline: none;
      padding: 5px;
      &:hover {
        transition: all 0.3s ease-in-out;
        background: $black-4;
      }
      &.is-current {
        pointer-events: none;
        font-weight: 600;
        background: $black-4;
      }
    }
  }
  &__selector {
    position: relative;
    margin-right: 3em;
    display: flex;
    align-items: center;
    color: $black-54;
    &__content {
      position: relative;
      & > a {
        color: $black-54;
        border: 1px solid palette(grey, 600);
      }
    }
    &__title {
      display: block;
      color: $black-54;
      margin-right: 1em;
      @include font-size(12px);
    }
    ul {
      list-style: none;
      background: palette(white);
      padding: 0;
      display: block;
      position: absolute;
      bottom: 3em;
      left: 0;
      right: 0;
      box-shadow: $shadow;
      border-radius: $border-radius;
      li {
        &:first-child:hover a {
          border-top-left-radius: $border-radius;
          border-top-right-radius: $border-radius;
        }
        &:last-child:hover a {
          border-bottom-left-radius: $border-radius;
          border-bottom-right-radius: $border-radius;
        }
      }
      a {
        display: block;
        border-radius: 1px;
        margin: 2px;
        color: $black-54;
        &:hover {
          background: $black-4;
        }
      }
    }
    a {
      display: block;
      outline: none;
      text-decoration: none;
      background: palette(white);
      padding: 0.5em 1em;
      border-radius: $border-radius;
      .svg-icon {
        margin-left: 1em;
        margin-bottom: 2px;
      }
    }
  }
  &__info {
    margin-left: auto;
    margin-right: 0;
    color: $black-54;
    font-weight: 400;
    @include font-size(13px);
  }
}
</style>
