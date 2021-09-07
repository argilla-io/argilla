<template>
  <div class="pagination__container">
    <div v-click-outside="closePageSizeSelector" class="pagination__selector">
      <span class="pagination__selector__title">Page size:</span>
      <a href="#" @click="showOptions = !showOptions">
        {{ paginationSize }}
        <svgicon name="drop-down" width="12" height="12" />
      </a>
      <ul v-if="showOptions">
        <li>
          <a
            v-for="item in availableItemsPerPage.filter(
              (i) => i !== paginationSize
            )"
            :key="item"
            href="#"
            @click.prevent="changePageSize(item)"
            >{{ item }}</a
          >
        </li>
      </ul>
    </div>
    <div class="pagination" v-if="totalItems > paginationSize">
      <a
        href="#"
        class="pagination__arrow pagination__arrow--prev"
        :class="currentPage <= 1 ? 'is-disabled' : null"
        @click.prevent="prevPage"
      >
        <svgicon name="chev-left" width="14" height="14" />
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
        <svgicon name="chev-right" width="14" height="14" />
      </a>
    </div>
    <div class="pagination__info">
      <strong>Records:</strong>
      {{ paginationSize * currentPage - (paginationSize - 1) }} -
      {{
        paginationSize * currentPage > totalItems
          ? totalItems
          : paginationSize * currentPage
      }}
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
    totalPages: {
      type: Number,
      default: 5,
    },
    totalItems: {
      type: Number,
    },
    currentPage: {
      type: Number,
      default: 1,
    },
    rangeOfPages: {
      type: Number,
      default: 2,
    },
    paginationSize: {
      type: Number,
      default: 20,
    },
    availableItemsPerPage: {
      type: Array,
      default: () => [5, 20, 50],
    },
  },
  data() {
    return {
      showOptions: false,
    };
  },
  computed: {
    pages() {
      let start = this.currentPage - this.rangeOfPages;
      start = start > 0 ? start : 1;
      let end = this.currentPage + this.rangeOfPages;
      end = end < this.totalPages ? end : this.totalPages;
      var pages = [];
      for (var i = start; i <= end; i++) {
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
    padding-bottom: 3em;
  }
  &__arrow {
    color: palette(grey, medium);
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 10px * 5;
    padding: 0 10px * 2.5;
    transition: color 200ms ease-in-out;
    outline: none;
    &.is-disabled {
      pointer-events: none;
      opacity: 0.4;
    }
  }
  &__numbers {
    display: flex;
    align-items: center;
    list-style: none;
    padding-left: 0;
    #{$self}__number {
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      width: 10px * 5;
      height: 10px * 5;
      outline: none;
      &:hover {
        color: palette(grey, medium);
      }
      &.is-current {
        color: white;
        background: palette(grey, medium);
      }
    }
  }
  &__selector {
    position: relative;
    margin-right: 3em;
    &__title {
      display: block;
      margin-bottom: 0.5em;
    }
    ul {
      list-style: none;
      background: $lighter-color;
      padding: 0;
      display: inline-block;
      position: absolute;
      top: 50px;
      left: 0;
      a {
        display: inline;
      }
    }
    a {
      outline: none;
      display: block;
      text-decoration: none;
      background: $lighter-color;
      padding: 0.5em 1em;
      .svg-icon {
        margin-left: 1em;
      }
    }
  }
  &__info {
    margin-left: auto;
    margin-right: 0;
  }
}
</style>
