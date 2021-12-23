<template>
  <div>
    <div class="rule__area">
      <div :class="[query ? 'active' : null, 'rule__container']">
        <rule-labels-definition
          :current-rule="currentRule"
          :dataset="dataset"
          @update-rule="updateRule"
        />
      </div>
      <div class="rule__global-metrics">
        <p class="global-metrics__title">Overall Metrics</p>
        <rules-overall-metrics v-if="rules.length > 0" :key="refresh" :rules="rules" :dataset="dataset" />
        <re-button
          class="rule__button button-quaternary--outline"
          @click="showRulesList"
          >Manage rules</re-button
        >
      </div>
    </div>
    <p class="rule__records" v-if="dataset.results.total > 0">Records ({{ dataset.results.total | formatNumber }})</p>
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
      currentRule: undefined,
      refresh: 0,
    };
  },
  async fetch() {
    this.rules = await this.getRules({ dataset: this.dataset });
    this.currentRule = await this.getRule({
      dataset: this.dataset,
      query: this.query,
    });
  },
  computed: {
    query() {
      return this.dataset.query.text;
    },
  },
  watch: {
    async query(n, o) {
      if (o !== n) {
        await this.$fetch();
        this.refresh++;
      }
    },
  },
  methods: {
    async showRulesList() {
      await this.dataset.viewSettings.enableRulesSummary();
    },
    async updateRule() {
      this.refresh++;
      await this.$fetch();
    },
    ...mapActions({
      getRule: "entities/text_classification/getRule",
      getRules: "entities/text_classification/getRules",
    }),
  },
};
</script>
<style lang="scss" scoped>
.rule {
  &__area {
    display: flex;
  }
  &__container {
    padding: 20px;
    background: rgba($lighter-color, 0.4);
    border: 1px solid $lighter-color;
    width: 100%;
    border-radius: 5px;
    margin-bottom: 2em;
    &.active {
      box-shadow: 0 1px 4px 0 rgba(185, 185, 185, 0.5);
    }
  }
  &__global-metrics {
    width: 290px;
    min-width: 290px;
    background: $primary-color;
    margin-left: 1em;
    color: $lighter-color;
    border-radius: 5px;
    margin-bottom: 2em;
    padding: 20px;
    .global-metrics {
      &__title {
        padding-bottom: 0;
        color: $lighter-color;
        @include font-size(22);
        font-weight: bold;
        margin-top: 0;
      }
    }
    &::v-deep {
      .rules-global__metrics p {
        width: 49%;
        margin-right: 0;
        color: $lighter-color;
        padding-bottom: 2em;
        @include font-size(14px);
        &[data-title] {
          &:after, &:before {
            display:none;
          }
        }
        span {
          color: $lighter-color;
          @include font-size(20px);
          margin-top: 0.3em;
        }
      }
    }
  }
  &__records {
    color: $font-secondary;
  }
  &__button {
    float: left;
    margin-bottom: 0 !important;
  }
}
</style>
