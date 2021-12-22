<template>
  <div>
    <div :class="[currentRule ? 'active' : null, 'rules__container']">
      <re-button
        class="rules__button button-secondary--outline"
        @click="showRulesList"
        >Manage rules</re-button
      >
      <rule-labels-definition
        :current-rule="currentRule"
        :dataset="dataset"
        @update-rule="updateRule"
      />
    </div>
    <p class="rules__records">Records ({{ dataset.results.total | formatNumber }})</p>
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
      currentRule: undefined,
    };
  },
  async fetch() {
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
      }
    },
  },
  methods: {
    async showRulesList() {
      await this.dataset.viewSettings.enableRulesSummary();
    },
    async updateRule() {
      await this.$fetch();
    },
    ...mapActions({
      getRule: "entities/text_classification/getRule",
    }),
  },
};
</script>
<style lang="scss" scoped>
.rules {
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
  &__records {
    color: $font-secondary;
  }
  &__button {
    float: right;
  }
}
</style>
