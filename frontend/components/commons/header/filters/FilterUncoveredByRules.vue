<template>
  <ReCheckbox
    @change="changeUncoveredByRules"
    class="re-checkbox--dark"
    :value="filter.selected"
  >
    Only records not covered by rules
  </ReCheckbox>
</template>

<script>
import { TextClassificationDataset } from "@/models/TextClassification";
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
  methods: {
    async changeUncoveredByRules() {
      const rulesId = this.dataset.rules.map((r) => r.query);
      this.$emit("apply", this.filter, !this.filter.selected ? rulesId : []);
    },
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
