<template>
  <div class="pagination__container">
    <div v-click-outside="closePageSizeSelector" class="pagination__selector">
      <span class="pagination__selector__title">Records per page:</span>
      <div class="pagination__selector__content">
        <a href="#" @click="showOptions = !showOptions">
          {{ paginationSize }}
          <svgicon name="drop-down" width="12" height="12" />
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
      Records:
      <strong>
        {{ paginationSize * currentPage - (paginationSize - 1) }}-{{
          paginationSize * currentPage > totalItems
            ? totalItems
            : paginationSize * currentPage
        }}
      </strong>
      of {{ totalItems }}
    </div>
  </div>
</template>
<script>
import "assets/icons/chev-left";
import "assets/icons/chev-right";
import "assets/icons/drop-down";
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
      return this.paginationSettings.pageSizeOptions;
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
      for (var i = start;i <= end;i++) {
        pages.push(i);
      }
      return pages;
    },
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
  &__container {
    display: flex;
    align-items: center;
    padding-top: 3em;
    padding-bottom: 12em;
  }
  &__arrow {
    color: $lighter-color;
    background: $primary-color;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    height: $pagination-size;
    padding: 0 10px;
    transition: color 200ms ease-in-out;
    outline: none;
    border-radius: 3px;
    &:hover {
      background: darken($primary-color, 10%);
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
    #{$self}__number {
      color: $primary-color;
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      width: $pagination-size;
      height: $pagination-size;
      outline: none;
      &:hover {
        color: $font-secondary-dark;
      }
      &.is-current {
        color: $font-secondary-dark;
        border: 2px solid $font-secondary-dark;
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
      top: 2em;
      left: 0;
      right: 0;
      border: 2px solid $primary-color;
      a {
        display: block;
        color: $font-secondary-dark;
        &:hover {
          background: palette(grey, smooth);
          color: $secondary-color;
        }
      }
    }
    a {
      outline: none;
      display: block;
      text-decoration: none;
      background: $lighter-color;
      padding: 0.4em 1em;
      .svg-icon {
        fill: $primary-color;
        margin-left: 1em;
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
