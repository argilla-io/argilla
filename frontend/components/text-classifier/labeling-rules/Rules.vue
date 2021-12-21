<template>
  <div>
    <div :class="[currentRule ? 'active' : null, 'rules__container']">
      <re-button
        class="rules__button button-secondary--outline"
        @click="showRulesList"
        >Manage rules</re-button
      >
      <input
        v-model="description"
        :class="[isFocused ? 'focused' : null, 'rules__query']"
        @focus="isFocused = true"
        @blur="isFocused = false"
      />
      <rules-annotation-area
        :description="description"
        :current-rule="currentRule"
        :dataset="dataset"
        @update-rule="updateRule"
      />
    </div>
    <p>Records ({{ dataset.results.total | formatNumber }})</p>
  </div>
</template>
<script>
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
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
      isFocused: undefined,
      currentRule: undefined,
      description: undefined,
    };
  },
  async fetch() {
    this.currentRule = await this.getRule({
      dataset: this.dataset,
      query: this.query,
    });
    this.description = this.currentRule
      ? this.currentRule.description
      : this.query;
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
    updateRule() {
      this.$fetch();
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
  &__query {
    color: $font-secondary;
    @include font-size(18px);
    font-weight: 600;
    margin-top: 0;
    border: none;
    background: none;
    padding: 0;
    outline: none;
    @include input-placeholder {
      color: $font-secondary;
      font-weight: 600;
    }
    &.focused {
      color: $font-secondary-dark;
      @include input-placeholder {
        color: $font-secondary-dark;
      }
    }
  }
  &__button {
    float: right;
  }
}
</style>
