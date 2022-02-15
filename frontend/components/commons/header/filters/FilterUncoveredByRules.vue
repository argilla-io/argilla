<template>
  <ReCheckbox
    @change="changeUncoveredByRules"
    class="re-checkbox--dark"
    :value="filter.selected"
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
    filter: {
      type: Object,
      required: true,
    }
  },
  methods: {
    ...mapActions({
      search: "entities/datasets/search",
    }),
    async changeUncoveredByRules() {
      const rulesId = this.dataset.rules.map((r) => r.query);
      await this.search({
        dataset: this.dataset,
        query: { uncovered_by_rules: !this.filter.selected ? rulesId : [] },
      });
    }
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
