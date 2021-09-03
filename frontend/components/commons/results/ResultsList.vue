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
      <div v-for="item in visibleRecords" :key="item.id" class="list__li">
        <results-record v-if="item" :dataset="dataset" :item="item">
          <slot name="record" :record="item" />
        </results-record>
      </div>
      <RePagination
        :pagination-size="dataset.viewSettings.pagination.size"
        :total-items="dataset.results.total"
        :total-pages="
          Math.ceil(
            dataset.results.total / dataset.viewSettings.pagination.size
          )
        "
        :current-page="dataset.viewSettings.pagination.page"
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

  methods: {
    ...mapActions({
      paginate: "entities/datasets/paginate",
    }),
    onScroll() {
      if (this.$refs.scroll.scrollTop > 100) {
        document.getElementsByTagName("body")[0].classList.add("fixed-header");
      } else {
        document
          .getElementsByTagName("body")[0]
          .classList.remove("fixed-header");
      }
    },
    async onPagination(page, size) {
      this.$nextTick(() => {
        document.getElementById("scroll").scrollTop = 0;
      });
      this.paginate({
        dataset: this.dataset,
        from: page,
        size: size,
      });
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
  }
  &__li {
    padding-bottom: 2px;
    position: relative;
  }
}
</style>
