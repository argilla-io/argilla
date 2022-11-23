<template>
  <div class="rule__area">
    <div class="left-item">
      <RulesQueryToken
        :query="queryText"
        :isGlobalEntities="isGlobalEntities"
        :entities="filteredEntities"
        :recordLength="this.numberOfRecords"
        :rulesLength="numberOfRulesInDataset"
        :isManagedRulesBtnDisabled="isNoRuleInDataset"
        :isSaveRulesBtnDisabled="isSaveRulesBtnDisabled"
        @on-search-entity="
          (searchQuery) => $emit('on-search-entity', searchQuery)
        "
        @on-select-global-entity="onSelectGlobalEntity"
        @on-click-save-rule="saveRule"
        @on-click-view-rules="onClickViewRules"
        @on-click-go-to-annotation-mode="onClickGoToAnnotationMode"
        @on-click-cancel="onClickCancel"
      />
    </div>
    <RulesMetricsToken
      title="Rules Metrics"
      :subcardInputs="options"
      btnLabel="Manage rules"
      backgroundColor="rgba(0,0,0,.04)"
      backgroundSubcardColor="rgba(0,0,0,.04)"
      textColor="#141414"
      textSubcardColor="#141414"
      borderColor="rgba(0,0,0,.04)"
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
    isGlobalEntities: {
      type: Boolean,
      required: true,
    },
    isSaveRulesBtnDisabled: {
      type: Boolean,
      required: true,
    },
    filteredEntities: {
      type: Array,
      required: true,
    },
    numberOfRecords: {
      type: Number,
    },
    numberOfRulesInDataset: {
      type: Number,
      required: false,
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
    onClickViewRules() {
      this.$emit("on-click-view-rules");
    },
    onClickCancel() {
      this.$emit("on-click-cancel");
    },
    saveRule() {
      this.$emit("on-saving-rule");
    },
    onClickGoToAnnotationMode() {
      this.$emit("on-click-go-to-annotation-mode");
    },
    onSelectGlobalEntity(id) {
      this.$emit("on-select-global-entity", id);
    },
  },
  computed: {
    ruleMetrics() {
      if (this.rule) return this.rule.rule_metrics;
    },
    isNoRuleInDataset() {
      return this.numberOfRulesInDataset === 0;
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
