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
        :isCancelBtnDisabled="isCancelBtnDisabled"
        :isRuleAlreadySaved="isRuleAlreadySaved"
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
      rulesMetricType="info"
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
    isCancelBtnDisabled: {
      type: Boolean,
      required: true,
    },
    isRuleAlreadySaved: {
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
      OptionsForRuleMetrics: null,
      options: [],
      initialParamsForInstance: {
        coverage: null,
        coverageAnnotated: null,
        totalRecords: null,
        annotatedRecords: null,
      },
    };
  },
  mounted() {
    this.OptionsForRuleMetrics = new OptionsForRuleMetrics(
      this.initialParamsForInstance,
      "TOKEN_ANNOTATION"
    );
    this.options = this.OptionsForRuleMetrics.getOptions();
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
    setOptions(params = this.initialParamsForInstance) {
      this.OptionsForRuleMetrics.setMetrics(params);
      this.options = this.OptionsForRuleMetrics.getOptions();
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
        const paramsForInstance = {
          coverage: newValue.coverage,
          coverageAnnotated: newValue.coverage_annotated,
          totalRecords: newValue.total_records,
          annotatedRecords: newValue.annotated_records,
        };

        this.setOptions(paramsForInstance);
      } else {
        this.setOptions();
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
  margin-bottom: 2em;
}
.left-item {
  display: flex;
  flex: 1;
}
</style>
