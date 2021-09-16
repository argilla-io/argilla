<template>
  <div v-if="annotation.length || prediction.length">
    <re-tabs
      :tabs="availableTabs"
      :active-tab="showTab"
      @change-tab="onChangeTab"
    >
      <div>
        <template v-if="showTab === 'Prediction'">
          <text-2-text-list :show-score="true" :list="prediction" />
        </template>
        <template v-if="showTab === 'Annotation'">
          <text-2-text-list :list="annotation" />
        </template>
      </div>
    </re-tabs>
  </div>
</template>
<script>
import "assets/icons/chev-left";
import "assets/icons/chev-right";
export default {
  props: {
    annotation: {
      type: Array,
      required: true,
    },
    prediction: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    showTab: "Prediction",
    predictionNumber: 0,
  }),
  mounted() {
    this.showTab = this.availableTabs.includes('Prediction') ? 'Prediction' : 'Annotation'
  },
  computed: {
    availableTabs() {
      let tabs = [];
      if (this.prediction.length) {
        tabs.push("Prediction");
      }
      if (this.annotation.length) {
        tabs.push("Annotation");
      }
      return tabs;
    },
  },
  methods: {
    onChangeTab(tab) {
      this.showTab = tab;
    },
    showPredictionNumber(index) {
      this.predictionNumber = index;
    },
    decorateScore(score) {
      return score * 100;
    },
  },
};
</script>
<style lang="scss" scoped></style>
