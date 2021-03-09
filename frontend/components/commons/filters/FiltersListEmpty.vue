<template>
  <div id="SearchFilterList" class="filters__container grid">
    <div class="filters">
      <div
        v-for="filter in this.computedDummyFilters"
        :key="filter.id"
        class="filter disabled"
      >
        <div class="filter__dummy">
          {{ filter.id }}
        </div>
      </div>
    </div>
    <div class="filters--right">
      <div v-if="enviroment === 'explore'" class="filter disabled show-more">
        More filters
      </div>
      <div class="filter disabled filter__sort">Sort by</div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    enviroment: {
      type: String,
      default: "explore",
    },
  },
  data: () => ({
    filtersDummies: {
      explore: [
        { id: "Annotated As" },
        { id: "Predicted As" },
        { id: "Confusion matrix" },
        { id: "Confidence" },
      ],
      feedback: [
        { id: "Annotated As" },
        { id: "Predicted As" },
        { id: "Confidence" },
        { id: "Metadata" },
      ],
    },
    sortBy: "gold",
    sortByDir: "desc",
    filtersChanged: {},
    filtersNumber: undefined,
    showAllFilters: true,
  }),
  computed: {
    computedDummyFilters() {
      return this.filtersDummies[this.enviroment];
    },
  },
};
</script>

<style lang="scss" scoped>
// @import "@recognai/re-commons/src/assets/scss/components/filters.scss";
.show-more,
.filter__sort {
  display: flex;
  align-items: center;
  position: relative;
  min-width: 120px;
}
.show-more:after,
.filter {
  &__dummy {
    height: 100%;
    width: auto;
    height: 45px;
    border: 2px solid $line-smooth-color;
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    padding: 0 1em;
    -webkit-transition: all 0.2s ease;
    transition: all 0.2s ease;
    border-radius: 0;
    &:after {
      content: "";
      border-color: #4a4a4a;
      border-style: solid;
      border-width: 1px 1px 0 0;
      display: inline-block;
      height: 8px;
      width: 8px;
      -webkit-transform: rotate(133deg);
      transform: rotate(133deg);
      -webkit-transition: all 1.5s ease;
      transition: all 1.5s ease;
      margin-bottom: 2px;
      margin-left: auto;
      margin-right: 0;
    }
  }
  &__sort:after {
    content: "";
    border-color: #4a4a4a;
    border-style: solid;
    border-width: 1px 1px 0 0;
    display: inline-block;
    height: 8px;
    width: 8px;
    -webkit-transform: rotate(133deg);
    transform: rotate(133deg);
    -webkit-transition: all 1.5s ease;
    transition: all 1.5s ease;
    margin-bottom: 2px;
    margin-left: auto;
    margin-right: 0;
  }
}
</style>
