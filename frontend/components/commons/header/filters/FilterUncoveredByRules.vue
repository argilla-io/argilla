<template>
  <base-checkbox
    @change="changeUncoveredByRules"
    class="re-checkbox--dark"
    :value="filter.selected"
  >
    Only records not covered by rules
  </base-checkbox>
</template>

<script>
import { TextClassificationDataset } from "@/models/TextClassification";
import { getQueryRuleArrayByDatasetNameAndWorkspace } from "@/models/rule-model/rule.queries";

export default {
  props: {
    dataset: {
      type: TextClassificationDataset,
      required: true,
    },
    filter: {
      type: Object,
      required: true,
    },
  },
  computed: {
    datasetName() {
      return this.dataset.name;
    },
    datasetWorkspace() {
      return this.dataset.workspace;
    },
    queriesFromRules() {
      const { datasetName, datasetWorkspace } = this;
      return getQueryRuleArrayByDatasetNameAndWorkspace({
        datasetName,
        datasetWorkspace,
      });
    },
  },
  methods: {
    async changeUncoveredByRules() {
      this.$emit(
        "apply",
        this.filter,
        !this.filter.selected ? this.queriesFromRules : []
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.re-checkbox {
  flex-direction: row-reverse;
  margin-left: 2em;
  @include font-size(13px);
  :deep(.checkbox-label) {
    margin-left: $base-space;
  }
}
</style>
