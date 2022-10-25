<template>
  <div class="rule__area">
    <div class="left-item">
      <RulesQueryToken title="New query" :recordsValue="10" />
    </div>
    <RulesMetricsToken
      title="Rules Metrics"
      :subcardInputs="options"
      btnLabel="Manage rules"
      @onClickBottomBtn="goToManageRules()"
      backgroundColor="#E84242"
      backgroundSubcardColor="white"
      textSubcardColor="#E84242"
      :isBtnDisabled="isManageRulesButtonDisabled"
    />
  </div>
</template>

<script>
import RulesMetricsToken from "./rules-metric/RulesMetricToken.component.vue";
import RulesQueryToken from "./rules-query/RulesQueryToken.component.vue";
import OptionsForRuleMetrics from "./OptionsForRuleMetrics.class";
export default {
  name: "RuleDefinitionToken",
  props: {
    queryText: {
      type: String,
      required: true,
    },
    rule: {
      type: Object,
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
    RulesQueryToken,
  },
  methods: {
    goToManageRules() {
      console.log("goToManageRules");
    },
  },
  computed: {
    ruleMetrics() {
      if (this.rule) return this.rule.rule_metrics;
    },
    isManageRulesButtonDisabled() {
      return this.rule.length === 0;
    },
  },
  watch: {
    ruleMetrics(newValue) {
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
  display: flex;
  flex: 1;
}
</style>
