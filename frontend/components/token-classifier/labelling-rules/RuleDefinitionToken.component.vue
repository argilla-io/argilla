<template>
  <div class="rule__area">
    <div class="left-item" v-if="queryText.length">
      <RulesQueryToken
        :title="`Query: ${queryText}`"
        :entities="entities"
        :recordLength="this.numberOfRecords"
        @on-search-entity="
          (searchQuery) => $emit('on-search-entity', searchQuery)
        "
        @on-click-save-rule="saveRule"
      />
    </div>
    <RulesMetricsToken
      title="Rules Metrics"
      :subcardInputs="options"
      btnLabel="Manage rules"
      @onClickBottomBtn="goToManageRules()"
      backgroundColor="rgba(0,0,0,.04)"
      backgroundSubcardColor="rgba(0,0,0,.04)"
      textColor="#141414"
      textSubcardColor="#141414"
      borderColor="rgba(0,0,0,.04)"
      :isBtnDisabled="isManageRulesButtonDisabled"
    />
  </div>
</template>

<script>
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import RulesMetricsToken from "./rules-metric/RulesMetricToken.component.vue";
import RulesQueryToken from "./rules-query/RulesQueryToken.component.vue";
import OptionsForRuleMetrics from "./OptionsForRuleMetrics.class";
import { getDatasetModelPrimaryKey } from "@/models/Dataset";

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
    entities: {
      type: Array,
      required: true,
    },
    numberOfRecords: {
      type: Number,
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
      DatasetViewSettings.update({
        where: getDatasetModelPrimaryKey,
        data: {
          visibleRulesList: true,
        },
      });
    },
    saveRule() {
      this.$emit("on-saving-rule");
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
