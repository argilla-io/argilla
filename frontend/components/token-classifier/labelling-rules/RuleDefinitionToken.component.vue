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
        :showButtons="showButtons"
        :message="message"
        @on-search-entity="(searchQuery) => onEmitSearchEntity(searchQuery)"
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
      ruleMetricsType="info"
    />
  </div>
</template>

<script>
import RulesMetricsToken from "./rules-metric/RuleMetricsToken.component.vue";
import RulesQueryToken from "./rules-query/RulesQueryToken.component.vue";
import OptionsForRuleMetrics from "./OptionsForRuleMetrics.class";
import { PROPERTIES } from "./labellingRules.properties";

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
    ruleStatus: {
      type: String || null,
      default: () => null,
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
      RULE_STATUS: PROPERTIES.RULE_STATUS,
      RULE_IS_ALREADY_SAVED: PROPERTIES.RULE_IS_ALREADY_SAVED,
      RULE_IS_SAVED: PROPERTIES.RULE_IS_SAVED,
      initialParamsForInstance: {
        coverage: null,
        coverageAnnotated: null,
        totalRecords: null,
        annotatedRecords: null,
      },
    };
  },
  mounted() {
    this.onEmitSearchEntity();
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
    onEmitSearchEntity(searchEntity = "") {
      this.$emit("on-search-entity", searchEntity);
    },
  },
  computed: {
    ruleMetrics() {
      if (this.rule) return this.rule.rule_metrics;
    },
    isNoRuleInDataset() {
      return this.numberOfRulesInDataset === 0;
    },
    showButtons() {
      if (
        this.ruleStatus === this.RULE_STATUS.ALREADY_SAVED ||
        this.ruleStatus === this.RULE_STATUS.IS_SAVED
      ) {
        return false;
      }
      return true;
    },
    message() {
      if (this.ruleStatus === this.RULE_STATUS.ALREADY_SAVED) {
        return this.RULE_IS_ALREADY_SAVED;
      } else if (this.ruleStatus === this.RULE_STATUS.IS_SAVED) {
        return this.RULE_IS_SAVED;
      }
      return "";
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
