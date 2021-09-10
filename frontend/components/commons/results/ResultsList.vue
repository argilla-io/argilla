<template>
  <div class="list">
    <slot name="header" />
    <VueAutoVirtualScrollList
      id="scroll"
      ref="scroll"
      :key="dataset.name"
      class="results-scroll"
      :default-height="100"
      :total-height="1200"
    >
      <div
        v-for="(item, index) in visibleRecords"
        :key="index"
        class="list__li"
      >
        <results-record v-if="item" :dataset="dataset" :item="item">
          <slot name="record" :record="item" />
        </results-record>
      </div>
      <RePagination
        :total-items="dataset.results.total"
        :pagination-settings="dataset.viewSettings.pagination"
        @changePage="onPagination"
      />
    </VueAutoVirtualScrollList>
  </div>
</template>
<script>
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      scrollComponent: undefined,
    };
  },
  computed: {
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
    moreDataAvailable() {
      return this.visibleRecords.length < this.dataset.results.total;
    },
  },
  mounted() {
    const scroll = document.getElementById("scroll");
    if (scroll) {
      this.scrollComponent = scroll;
      this.scrollComponent.addEventListener("scroll", this.onScroll);
    }
  },
  beforeDestroy() {
    if (this.scrollComponent)
      this.scrollComponent.removeEventListener("scroll", this.onScroll);
  },
  created() {
    window.addEventListener("keydown", this.keyDown);
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
  },
  methods: {
    ...mapActions({
      paginate: "entities/datasets/paginate",
    }),
    keyDown(event) {
      let { page, size } = this.dataset.viewSettings.pagination;
      if (event.keyCode === 39 && page < this.dataset.results.total / size) {
        this.onPagination(page + 1, size);
      } else if (event.keyCode === 37 && page > 1) {
        this.onPagination(page - 1, size);
      }
    },
    onScroll() {
      if (this.$refs.scroll.scrollTop > 10) {
        document.getElementsByTagName("body")[0].classList.add("fixed-header");
      } else {
        document
          .getElementsByTagName("body")[0]
          .classList.remove("fixed-header");
      }
    },
    async onPagination(page, size) {
      await this.paginate({
        dataset: this.dataset,
        page: page,
        size: size,
      });
      document.getElementById("scroll").scrollTop = 0;
    },
  },
};
</script>
<style lang="scss" scoped>
.list {
  $this: &;
  padding: 0;
  width: 100%;
  position: relative;
  margin-bottom: 0;
  list-style: none;
  .results-scroll {
    padding-top: 1em;
    height: 100vh !important;
    overflow: auto;
    padding-left: 4em;
    padding-right: calc(4em + 45px);
    @include media(">desktopLarge") {
      width: 100%;
      padding-right: calc(294px + 45px + 4em);
    }
  }
  &__li {
    padding-bottom: 2px;
    position: relative;
  }
}
</style>
