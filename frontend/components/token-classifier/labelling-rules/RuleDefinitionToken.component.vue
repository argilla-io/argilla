<template>
  <div class="rule__area">
    <div class="left-item">RuleDefinition</div>
    <RulesMetricsToken
      title="Rules Metrics"
      :subcardInputs="options"
      btnLabel="Manage rules"
      @onClickBottomBtn="goToManageRules()"
    />

    <pre>{{ ruleByQueryAndByDataset_id }}</pre>
    <!-- <pre>{{ ruleMetrics }}</pre> -->
  </div>
</template>

<script>
import Rule from "../../../models/token-classification/Rule.modelTokenClassification";
import { TokenClassificationDataset } from "../../../models/TokenClassification";
import RulesMetricsToken from "./RulesMetricsToken.component.vue";
import OptionsForRuleMetrics from "./OptionsForRuleMetrics.class";
export default {
  name: "RuleDefinitionToken",
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      options: [],
    };
  },
  components: {
    RulesMetricsToken,
  },
  methods: {
    goToManageRules() {
      console.log("goToManageRules");
    },
  },
  computed: {
    queryText() {
      return TokenClassificationDataset.find([
        this.datasetId[0],
        this.datasetId[1],
      ]).query.text;
    },
    ruleByQueryAndByDataset_id() {
      return Rule.query()
        .where("author", this.datasetId[0])
        .where("name", this.datasetId[1])
        .where("query", this.queryText)
        .with("rule_metrics")
        .first();
    },
    ruleMetrics() {
      if (
        this.ruleByQueryAndByDataset_id &&
        this.ruleByQueryAndByDataset_id.rule_metrics
      ) {
        return this.ruleByQueryAndByDataset_id.rule_metrics;
      }
    },
  },
  watch: {
    ruleMetrics(newValue, oldValue) {
      if (newValue) {
        const optionsForInstance = {
          coverage: newValue.coverage,
          coverageAnnotated: newValue.coverage_annotated,
          totalRecords: newValue.total_records,
          annotatedRecords: newValue.annotated_records,
        };
        this.options = new OptionsForRuleMetrics(
          optionsForInstance,
          "TOKEN_ANNOTATION"
        ).getOptions();
      } else {
        this.options = [];
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.rule__area {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}
.left-item {
  flex: 1;
}
</style>
