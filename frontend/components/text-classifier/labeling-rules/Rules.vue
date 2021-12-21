<template>
  <div>
    <div :class="[currentRule ? 'active' : null, 'rules__container']">
      <re-button
        class="rules__button button-secondary--outline"
        @click="showRulesList"
      >Manage rules</re-button>
      <p class="rules__query">{{query}}</p>
      <rules-annotation-area :currentRule="currentRule" :dataset="dataset" @update-rule="updateRule"/>
    </div>
    <p>Records ({{dataset.results.total | formatNumber}})</p>
  </div>
</template>
<script>
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { mapActions } from "vuex";
export default {
  computed: {
    query() {
      return this.dataset.query.text;
    }
  },
  data: () => {
    return {
      currentRule: undefined,
    }
  },
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
  },
  async fetch() {
    this.currentRule = await this.getRule({
      dataset: this.dataset,
      query: this.query
    });
  },
  watch: {
    async query(n, o) {
      if (o !== n) {
        await this.$fetch()
      }
    }
  },
  methods: {
    showRulesList() {
      DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          visibleRulesList: true,
        },
      });
    },
    updateRule() {
      this.$fetch()
    },
    ...mapActions({
      getRule: "entities/text_classification/getRule",
    }),
  }
};
</script>
<style lang="scss" scoped>
.rules {
  &__container {
    padding: 20px;
    background: rgba($lighter-color, .4);
    border: 1px solid $lighter-color;
    width: 100%;
    border-radius: 5px;
    margin-bottom: 2em;
    &.active {
      box-shadow: 0 1px 4px 0 rgba(185,185,185,0.50);
    }
  }
  &__query {
    color: $font-secondary;
    @include font-size(18px);
    font-weight: 600;
    margin-top: 0;
  }
  &__button {
    float: right;
  }
}
</style>


