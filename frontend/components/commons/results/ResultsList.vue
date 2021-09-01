<template>
  <div class="list">
    <slot name="header" />
    <VueAutoVirtualScrollList
      id="scroll"
      ref="scroll"
      :key="dataset.name"
      style="width: 100%"
      class="virtual-scroll"
      :total-height="1200"
      :default-height="100"
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
      <ReShowMoreData
        v-if="moreDataAvailable"
        :items="visibleRecords.length"
        :total="dataset.results.total"
        :more-data-size="dataset.viewSettings.pagination.size"
        @moredata="onShowMoreData"
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
      fetchMoreRecords: "entities/datasets/fetchMoreRecords",
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
    async onShowMoreData() {
      this.fetchMoreRecords({
        dataset: this.dataset,
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
  .virtual-scroll {
    padding-top: 1em;
    height: 100vh !important;
  }
  &__li {
    padding-bottom: 2px;
    position: relative;
  }
}
</style>
