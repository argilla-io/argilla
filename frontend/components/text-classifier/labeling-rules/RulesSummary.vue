<template>
  <div v-if="isVisible" class="rules-summary">
    <ReLoading v-if="$fetchState.pending" />
    <div v-else-if="!$fetchState.error" class="rules-summary__container">
      <re-button @click="hideList()" class="rules-summary__close button-quaternary">
        <svgicon
          name="chev-left"
          width="12"
          height="12"
        ></svgicon>Back to query view</re-button>
      <p class="rules-summary__title">Overall Metrics</p>
      <rules-summary-metrics :rules="rules" :dataset="dataset" />
      <p class="rules-summary__title">Rules</p> 
      <ReSearchBar @input="onSearch" v-if="formattedRules.length" placeholder="Search rule by name" />
      <ReTableInfo
        class="rules-summary__table"
        :data="formattedRules"
        :sorted-order="sortedOrder"
        :sorted-by-field="sortedByField"
        :columns="tableColumns"
        :actions="actions"
        :query-search="querySearch"
        :global-actions="false"
        search-on="name"
        :noDataInfo="noDataInfo"
        :emptySeachInfo="emptySeachInfo"
        :show-modal="showModal"
        :delete-modal-content="getDeleteModalText"
        @sort-column="onSortColumns"
        @onActionClicked="onActionClicked"
        @close-modal="closeModal"
      />
      <re-button v-if="formattedRules.length" class="button-primary" @click="updateSummary()">Update Summary</re-button>
    </div>
  </div>
</template>
<script>
import "assets/icons/empty-rules";
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
      querySearch: undefined,
      showModal: undefined,
      rules: [],
      metricsByLabel: {},
      tableColumns: [
        {
          name: "Name",
          field: "name",
          class: "table-info__title",
          type: "action",
        },
        { name: "Label", field: "label", class: "text" },
        { name: "Coverage", field: "coverage", class: "text", type: "number" },
        {
          name: "Annot. Cover.",
          field: "coverage_annotated",
          class: "text",
          type: "number",
        },
        { name: "Correct", field: "correct", class: "text" },
        { name: "Incorrect", field: "incorrect", class: "text" },
        {
          name: "Precision",
          field: "precision",
          class: "text",
          type: "number",
        },
      ],
      sortedOrder: "desc",
      sortedByField: "query",
      actions: [{ name: "delete", icon: "delete", title: "Delete dataset" }],
      noDataInfo: {
        title: '0 rules defined',
        message: `You have not defined any rules for this dataset yet.`,
        icon: 'empty-rules',
      },
      emptySeachInfo: {
        title: '0 rules found',
      },
    };
  },
  async fetch() {
    this.rules = await this.getRules({ dataset: this.dataset });
    await this.getMetricsByLabel();
  },
  computed: {
    isVisible() {
      return this.dataset.viewSettings.visibleRulesList;
    },
    formattedRules() {
      return this.rules.map((r) => {
        return {
          name: r.description,
          query: r.query,
          kind: "select",
          label: r.label,
          coverage: this.metricsByLabel[r.query].coverage,
          coverage_annotated: this.metricsByLabel[r.query].coverage_annotated,
          correct: this.metricsByLabel[r.query].correct,
          incorrect: this.metricsByLabel[r.query].incorrect,
          precision: this.metricsByLabel[r.query].precision,
        };
      });
    },
    getDeleteModalText() {
      return {
        title: 'Permanently delete rule',
        text: `You are about to delete the rule <strong>"${this.showModal}"</strong> from your dataset. This action cannot be undone.`
      };
    },
  },
  mounted() {
    document.getElementsByTagName("body")[0].classList.remove("fixed-header");
  },
  methods: {
    ...mapActions({
      search: "entities/datasets/search",
      getRules: "entities/text_classification/getRules",
      deleteRule: "entities/text_classification/deleteRule",
      getRuleMetricsByLabel:
        "entities/text_classification/getRuleMetricsByLabel",
    }),
    async hideList() {
      await this.dataset.viewSettings.disableRulesSummary();
    },

    async getMetricsByLabel() {
      const responses = await Promise.all(
        this.rules.map((rule) => {
          return this.getRuleMetricsByLabel({
            dataset: this.dataset,
            query: rule.query,
            label: rule.label,
          });
        })
      );

      responses.forEach((response, idx) => {
        this.metricsByLabel[this.rules[idx].query] = response;
      });
    },
    async onSelectQuery(id) {
      if (id.query !== this.dataset.query.text) {
        await this.search({ dataset: this.dataset, query: { text: id.query } });
      }
      await this.hideList();
    },
    onActionClicked(action, rowId) {
      console.log(action, rowId);
      switch (action) {
        case "delete":
          this.onShowConfirmRuleDeletion(rowId);
          break;
        case "confirm-delete":
          this.onDeleteRule(rowId);
          break;
        case "select":
          this.onSelectQuery(rowId);
          break;
        default:
          console.warn(action);
      }
    },
    onSortColumns(by, order) {
      this.sortedByField = by;
      this.sortedOrder = order;
    },
    onSearch(event) {
      this.querySearch = event;
    },
    async updateSummary() {
      await this.getMetricsByLabel();
    },
    onShowConfirmRuleDeletion(id) {
      this.showModal = id.name;
    },
    async onDeleteRule(id) {
      this.closeModal();
      await this.deleteRule({
        dataset: this.dataset,
        query: id.query,
      });
      await this.$fetch();
    },
    closeModal() {
      this.showModal = undefined;
    },
  },
};
</script>
<style lang="scss" scoped>
.rules-summary {
  padding-left: 4em;
  padding-top: 3em;
  overflow: auto;
  height: 100vh;
  &__container {
    margin-top: 3em;
    padding: 20px;
    background: rgba($lighter-color, .4);
    border: 1px solid $lighter-color;
    width: 100%;
    border-radius: 5px;
  }
  &__title {
    color: $font-secondary-dark;
    @include font-size(22px);
    font-weight: 600;
    margin-top: 0;
  }
  &__table {
    margin-bottom: 2em !important;
    ::v-deep {
      .table-info__item__col:nth-of-type(2) {
        min-width: 100px;
      }
      .table-info__item__col:first-child {
        min-width: 120px;
      }
      .table-info__body {
        overflow: visible;
        height: auto;
      }
      .table-info__item {
        padding-right: 3em !important;
      }
    }
  }
  &__close {
    float: right;
  }
}
</style>
