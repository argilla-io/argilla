<template>
  <div>
    <div class="rule__area">
      <div :class="[query ? 'active' : null, 'rule__container']">
        <rule-empty-query :dataset="dataset" v-if="!query" />
        <rule-labels-definition
          v-else
          :current-rule="currentRule"
          :dataset="dataset"
          @update-rule="updateRule"
          @update-labels="updateLabels"
        >
          <template v-if="recordsMetric" #records-metric>
            Records
            <strong>
              {{ recordsMetric.value }}
            </strong>
          </template>
        </rule-labels-definition>
      </div>
      <div class="rule__metrics">
        <rules-metrics
          @records-metric="onUpdateRecordsMetric"
          title="Rule Metrics"
          metrics-type="all"
          :activeLabel="activeLabel"
          :key="refresh"
          :rules="rules"
          :dataset="dataset"
        >
          <template #button-bottom>
            <re-button
              class="rule__button button-quaternary--outline"
              @click="showRulesList"
              >Manage rules</re-button
            >
          </template>
        </rules-metrics>
      </div>
    </div>
    <p class="rule__records" v-if="dataset.results.total > 0">
      Records ({{ dataset.results.total | formatNumber }})
    </p>
  </div>
</template>
<script>
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
  },
  data: () => {
    return {
      rules: [],
      selectedLabels: [],
      currentRule: undefined,
      recordsMetric: undefined,
      refresh: 0,
    };
  },
  async fetch() {
    await this.getAllRules();
    this.currentRule = await this.getRule({
      dataset: this.dataset,
      query: this.query,
    });
  },
  computed: {
    query() {
      return this.dataset.query.text;
    },
    activeLabel() {
      return this.selectedLabels.length ? this.selectedLabels[0] : undefined;
    },
  },
  watch: {
    async query(n, o) {
      if (o !== n) {
        this.refresh++;
        await this.$fetch();
      }
    },
  },
  methods: {
    async getAllRules() {
      this.rules = await this.getRules({ dataset: this.dataset });
    },
    async showRulesList() {
      await this.dataset.viewSettings.enableRulesSummary();
    },
    async updateRule() {
      await this.$fetch();
    },
    updateLabels(labels) {
      this.selectedLabels = labels;
    },
    onUpdateRecordsMetric(met) {
      this.recordsMetric = met;
    },
    ...mapActions({
      getRules: "entities/text_classification/getRules",
      getRule: "entities/text_classification/getRule",
    }),
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
  &__records {
    color: $font-secondary;
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
