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
    <div v-click-outside="closePageSizeSelector" class="pagination__selector">
      <span class="pagination__selector__title">Records per page:</span>
      <div class="pagination__selector__content">
        <a href="#" @click="showOptions = !showOptions">
          {{ paginationSize }}
          <svgicon name="drop-up" width="12" height="12" />
        </a>
        <ul v-if="showOptions">
          <li>
            <a
              v-for="item in availableItemsPerPage"
              :key="item"
              href="#"
              @click.prevent="changePageSize(item)"
              >{{ item }}</a
            >
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
        <svgicon name="chev-left" width="8" height="8" /> Prev
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
        Next <svgicon name="chev-right" width="8" height="8" />
      </a>
    </div>
    <div class="pagination__info">
      <strong>
        {{ paginationSize * currentPage - (paginationSize - 1) }}-{{
          paginationSize * currentPage > totalItems
            ? totalItems
            : paginationSize * currentPage
        }}
      </strong>
      of {{ totalItems | formatNumber }}
    </div>
  </div>
</template>
<script>
import "assets/icons/chev-left";
import "assets/icons/chev-right";
import "assets/icons/drop-up";
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
    allowKeyboardPagination: {
      type: Boolean,
      required: true,
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
      return Math.ceil(this.totalItems / this.paginationSettings.size);
    },
    paginationSize() {
      return this.paginationSettings.size;
    },
    availableItemsPerPage() {
      return this.paginationSettings.pageSizeOptions.filter(p => p !== this.paginationSize);
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
  },
  created() {
    window.addEventListener("keydown", this.keyDown);
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
    changePage(n) {
      this.$emit("changePage", n, this.paginationSize);
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
      if (this.allowKeyboardPagination) {
        if (event.keyCode === 39) {
          this.nextPage()
        } else if (event.keyCode === 37) {
          this.prevPage()
        }
      }
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
  font-weight: 600;
  &__container {
    padding-left: 4em;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    background: palette(grey, light);
    border-top: 1px solid palette(grey, smooth);
    padding-right: calc(4em + 45px);
    min-height: 63px;
    @include media(">desktopLarge") {
      width: 100%;
      padding-right: calc(294px + 45px + 4em);
    }
  }
  &__arrow {
    transition: all 0.3s ease-in-out;
    color: $font-secondary;
    background: transparent;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    height: $pagination-size;
    padding: 0 10px;
    transition: color 200ms ease-in-out;
    outline: none;
    border-radius: 3px;
    svg {
      margin-top: 1px;
    }
    &:hover {
      transition: all 0.3s ease-in-out;
      background: palette(grey, smooth);
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
      opacity: 0;
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
      color: $font-secondary;
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      min-width: $pagination-size;
      height: $pagination-size;
      margin: auto 0.5em;
      outline: none;
      padding: 5px;
      &:hover {
        transition: all 0.3s ease-in-out;
        background: palette(grey, smooth);
      }
      &.is-current {
        pointer-events: none;
        color: $font-secondary-dark;
        font-weight: 700;
        background: palette(grey, smooth);
      }
    }
  }
  &__selector {
    position: relative;
    margin-right: 3em;
    display: flex;
    align-items: center;
    &__content {
      position: relative;
      & > a {
        color: $secondary-color;
        border: 1px solid palette(grey, smooth);
      }
    }
    &__title {
      display: block;
      margin-bottom: 0.5em;
      color: $font-secondary-dark;
      margin-right: 1em;
    }
    ul {
      list-style: none;
      background: $lighter-color;
      padding: 0;
      display: block;
      position: absolute;
      bottom: 3em;
      left: 0;
      right: 0;
      box-shadow: 0 5px 11px 0 rgba(0,0,0,0.50);
      border-radius: 3px;
      margin: 2px;
      a {
        display: block;
        color: $font-secondary-dark;
        border-radius: 1px;
        margin: 2px;
        &:hover {
          background: palette(grey, smooth);
        }
      }
    }
    a {
      display: block;
      outline: none;
      text-decoration: none;
      background: $lighter-color;
      padding: 0.5em 1em;
      .svg-icon {
        fill: $primary-color;
        margin-left: 1em;
        margin-bottom: 2px;
      }
    }
  }
  &__info {
    margin-left: auto;
    margin-right: 0;
    color: $font-secondary-dark;
  }
}
</style>
