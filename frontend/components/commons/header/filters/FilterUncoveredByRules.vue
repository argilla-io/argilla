<template>
  <ReCheckbox
    :id="showUncoveredByRules"
    v-model="showUncoveredByRules"
    class="re-checkbox--dark"
    :value="showUncoveredByRules"
  >
    Not covered by rules
  </ReCheckbox>
</template>

<script>
import { TextClassificationDataset } from "@/models/TextClassification";
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      type: TextClassificationDataset,
      required: true,
    },
  },
  data: () => {
    return {
      showUncoveredByRules: false,
    };
  },
  watch: {
    async showUncoveredByRules() {
      if (this.showUncoveredByRules) {
        const rulesId = this.dataset.rules.map((r) => r.query);
        await this.search({
          dataset: this.dataset,
          query: { uncovered_by_rules: rulesId },
        });
      } else {
        await this.search({
          dataset: this.dataset,
          query: { uncovered_by_rules: [] },
        });
      }
    },
  },
  methods: {
    ...mapActions({
      search: "entities/datasets/search",
    }),
  },
};
</script>

<style lang="scss" scoped>
.re-checkbox {
  flex-direction: row-reverse;
  ::v-deep .checkbox-label {
    margin-left: 1em;
  }
}
</style>
