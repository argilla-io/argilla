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
        <rules-metrics
          title="Rule Metrics"
          metrics-type="all"
          :dataset="dataset"
        >
          <template #button-bottom>
            <re-button
              class="rule__button button-quaternary--outline"
              :disabled="isLoading"
              @click="showRulesList"
              >Manage rules</re-button
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
      await this.updateCurrentRule({
        query: newValue,
        label: (this.currentRule || {}).label,
      });
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
    async updateCurrentRule({ query, label }) {
      if (!query) {
        return await this.dataset.clearCurrentLabelingRule();
      }
      if (label) {
        await this.dataset.setCurrentLabelingRule({
          query,
          label,
        });
      } else {
        await this.dataset.setCurrentLabelingRule({
          query,
          label: undefined,
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
    background: rgba($lighter-color, 0.4);
    border: 1px solid $lighter-color;
    width: 100%;
    border-radius: 5px;
    &.active {
      box-shadow: 0 1px 4px 0 rgba(185, 185, 185, 0.5);
    }
  }
  &__button {
    float: left;
    align-self: flex-start;
    margin-bottom: 0 !important;
    margin-top: auto;
    clear: both;
  }
  &__metrics {
    min-width: 350px;
    @include media(">desktopLarge") {
      min-width: 33%;
    }
    &::v-deep {
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
