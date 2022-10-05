<template>
  <div>
    <div class="rule__area">
      <div :class="[query ? 'active' : null, 'rule__container']">
        <rule-empty-query :dataset="dataset" v-if="!query" />
        <rule-labels-definition
          v-else
          :dataset="dataset"
          :isSaved="saved"
          @save-rule="saveRule"
          @update-rule="updateCurrentRule"
        >
        </rule-labels-definition>
      </div>
      <div class="rule__metrics">
        <rules-metrics title="Rule Metrics" :dataset="dataset">
          <template #button-bottom>
            <base-button
              class="rule__button primary light"
              :disabled="isLoading"
              @click="showRulesList"
              >Manage rules</base-button
            >
          </template>
        </rules-metrics>
      </div>
    </div>
  </div>
</template>
<script>
import { TextClassificationDataset } from "@/models/TextClassification";
export default {
  props: {
    dataset: {
      type: TextClassificationDataset,
      required: true,
    },
  },
  data: () => {
    return {
      saved: undefined,
    };
  },
  async fetch() {
    if (!this.rules) {
      await this.dataset.refreshRules();
    }
    if (!this.hasMetrics) {
      await this.dataset.refreshRulesMetrics();
    }
    if (!this.currentRule && this.query) {
      const rule = this.dataset.findRuleByQuery(this.query, undefined);
      await this.dataset.setCurrentLabelingRule(
        rule ? rule : { query: this.query }
      );
    }
  },
  watch: {
    async query(newValue) {
      this.saved = false;
      const rule = this.dataset.findRuleByQuery(newValue, undefined);
      await this.dataset.setCurrentLabelingRule(
        rule
          ? rule
          : { query: newValue, labels: (this.currentRule || {}).labels }
      );
    },
  },
  computed: {
    query() {
      return this.dataset.query.text;
    },
    isLoading() {
      return this.$fetchState.pending;
    },
    currentRule() {
      return this.dataset.getCurrentLabelingRule();
    },
    hasMetrics() {
      return this.overalMetrics && this.rulesMetrics;
    },
    rules() {
      return this.dataset.labelingRules;
    },
    overalMetrics() {
      return this.dataset.labelingRulesOveralMetrics;
    },
    rulesMetrics() {
      return this.dataset.labelingRulesMetrics;
    },
  },
  methods: {
    async updateCurrentRule({ query, labels }) {
      if (!query) {
        return await this.dataset.clearCurrentLabelingRule();
      }
      if (labels) {
        await this.dataset.setCurrentLabelingRule({
          query,
          labels,
        });
      } else {
        await this.dataset.setCurrentLabelingRule({
          query,
          labels: [],
        });
      }
      this.saved = false;
    },
    async showRulesList() {
      await this.dataset.viewSettings.enableRulesSummary();
    },
    async saveRule(rule) {
      await this.dataset.storeLabelingRule(rule);
      this.saved = true;
    },
  },
};
</script>
<style lang="scss" scoped>
.rule {
  &__area {
    display: flex;
    margin-bottom: 2em;
  }
  &__container {
    padding: 20px;
    background: palette(white);
    box-shadow: $shadow-100;
    width: 100%;
    border-radius: $border-radius;
    // &.active {
    //   box-shadow: 0 1px 4px 0 rgba(185, 185, 185, 0.5);
    // }
  }
  &__button {
    float: left;
    align-self: flex-start;
    margin-top: auto;
    clear: both;
  }
  &__metrics {
    min-width: 350px;
    @include media(">desktopLarge") {
      min-width: 33%;
    }
    &:deep() {
      .rule-metrics__container {
        flex-wrap: wrap;
        height: 100%;
      }
      .rule-metrics__item {
        width: 49%;
        display: inline-block;
      }
    }
  }
}
</style>
