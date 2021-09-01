<template>
  <div>
    <p class="sidebar__title">Stats</p>
    <StatsSelector
      :selected-option="selectedOption"
      :options="options"
      @selectOption="onSelectOption"
    />
    <StatsErrorDistribution
      v-if="selectedOption.id === 'error'"
      :dataset="dataset"
    />
    <template v-if="selectedOption.id === 'keywords'">
      <div class="scroll">
        <div v-for="(counter, keyword) in getKeywords" :key="keyword">
          <div v-if="counter > 0" class="info">
            <label>{{ keyword }}</label>
            <span class="records-number">{{ counter }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  // TODO clean and typify
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => {
    return {
      selectedOption: {
        id: "keywords",
        name: "Keywords",
      },
    };
  },
  computed: {
    getKeywords() {
      return this.dataset.results.aggregations.words;
    },
    options() {
      let options = [];
      options.push({
        id: "keywords",
        name: "Keywords",
      });
      if (Object.values(this.dataset.results.aggregations.predicted).length) {
        options.push({
          id: "error",
          name: "Error Distribution",
        });
      }
      return options;
    },
  },
  methods: {
    onSelectOption(opt) {
      this.selectedOption = opt;
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  &__title {
    color: $font-secondary-dark;
    margin-top: 0.5em;
    @include font-size(20px);
  }
}
label {
  display: block;
  width: calc(100% - 40px);
  overflow: hidden;
  text-overflow: ellipsis;
}
.labels {
  margin-top: 3em;
  strong {
    margin-bottom: 1em;
    display: block;
  }
}
.info {
  position: relative;
  display: flex;
  margin-bottom: 0.7em;
  color: $font-secondary-dark;
}
.scroll {
  max-height: calc(100vh - 400px);
  padding-right: 1em;
  margin-right: -1em;
  overflow: auto;
}
.records-number {
  margin-right: 0;
  margin-left: auto;
}
</style>
