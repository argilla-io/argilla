<template>
  <div v-if="isVisible" class="rules-management">
    <div>
      <div class="rules-management__header">
        <p class="rules-management__title">
          Rules
          <span v-if="formattedRules.length"
            >({{ formattedRules.length }})</span
          >
        </p>
        <base-button
          class="rules-management__button primary outline small"
          @click="hideList"
        >
          <svgicon name="chevron-left" width="12" height="12"></svgicon>Back to
          query view</base-button
        >
      </div>
      <base-search-bar
        v-if="formattedRules.length"
        placeholder="Search rule by name"
        @input="onSearch"
      />
      <base-table-info
        class="rules-management__table"
        :data="formattedRules"
        :sorted-order="sortedOrder"
        :sorted-by-field="sortedByField"
        :columns="tableColumns"
        :actions="actions"
        :query-search="querySearch"
        :global-actions="false"
        search-on="query"
        :no-data-info="noDataInfo"
        :empty-search-info="emptySearchInfo"
        :visible-modal-id="visibleModalId"
        :delete-modal-content="getDeleteModalText"
        @sort-column="onSortColumns"
        @onActionClicked="onActionClicked"
        @close-modal="closeModal"
      />
    </div>
  </div>
</template>
<script>
import "assets/icons/unavailable";
import { mapActions } from "vuex";
import { TokenClassificationDataset } from "@/models/TokenClassification";
export default {
  props: {
    dataset: {
      type: TokenClassificationDataset,
      required: true,
    },
    rules: {
      type: Array,
    }
  },
  data: () => {
    return {
      querySearch: undefined,
      visibleModalId: undefined,
      isLoading: undefined,
      sortedOrder: "desc",
      sortedByField: "created_at",
      actions: [{ name: "delete", icon: "trash-empty", title: "Delete rule" }],
      noDataInfo: {
        title: "0 rules defined",
        message: `You have not defined any rules for this dataset yet.`,
        icon: "unavailable",
      },
      emptySearchInfo: {
        title: "0 rules found",
      },
    };
  },
  // async fetch() {
  //   if (!this.rules) {
  //     await this.dataset.refreshRules();
  //   }
  // },
  computed: {
    tableColumns() {
      return [
        {
          name: "Query",
          field: "query",
          class: "table-info__title",
          type: "action",
        },
        { name: "Labels", field: "labels", class: "array", type: "array" },
        {
          name: "Coverage",
          field: "coverage",
          class: "text",
          type: "percentage",
          tooltip: "Percentage of records labeled by the rule",
        },
        {
          name: this.$mq >= "sm" ? "An. Cover." : "Annot. Cover.",
          field: "coverage_annotated",
          class: "text",
          type: "percentage",
          tooltip: "Percentage of annotated records labeled by the rule",
        },
        {
          name: "Correct",
          field: "correct",
          class: "text",
          tooltip:
            "Number of labels the rule predicted correctly with respect to the annotations",
        },
        {
          name: "Incorrect",
          field: "incorrect",
          class: "text",
          tooltip:
            "Number of labels the rule predicted incorrectly with respect to the annotations",
        },
        {
          name: "Precision",
          field: "precision",
          class: "text",
          type: "percentage",
          tooltip:
            "Percentage of correct labels given by the rule with respect to the annotations",
        },
        {
          name: "Created at",
          field: "created_at",
          class: "date",
          type: "date",
        },
      ];
    },
    perRuleMetrics() {
      return this.dataset.labelingRulesMetrics;
    },
    isVisible() {
      return this.dataset.viewSettings.visibleRulesList;
    },
    formattedRules() {
      if (this.rules) {
        return this.rules.map((r) => {
          return {
            id: r.query,
            name: r.description,
            query: r.query,
            kind: "select",
            labels: r.labels,
            // ...this.metricsForRule(r),
            created_at: r.created_at,
          };
        });
      } else {
        return [];
      }
    },
    getDeleteModalText() {
      return {
        title: "Permanently delete rule",
        text: `You are about to delete the rule <strong>"${this.visibleModalId}"</strong> from your dataset. This action cannot be undone.`,
      };
    },
  },
  methods: {
    ...mapActions({
      search: "entities/datasets/search",
    }),
    // metricsForRule(rule) {
    //   const metrics = this.perRuleMetrics[rule.query];
    //   if (!metrics) {
    //     return {};
    //   }
    //   return {
    //     coverage: metrics.coverage,
    //     coverage_annotated: metrics.coverage_annotated,
    //     correct: metrics.correct,
    //     incorrect: metrics.incorrect,
    //     precision: !isNaN(metrics.precision) ? metrics.precision : "-",
    //   };
    // },

    async hideList() {
      await this.dataset.viewSettings.disableRulesSummary();
    },

    async onSelectQuery(rule) {
      await this.dataset.setCurrentLabelingRule(rule);
      if (rule.query !== this.dataset.query.text) {
        await this.search({
          dataset: this.dataset,
          query: { text: rule.query },
        });
      }
      await this.hideList();
    },
    onActionClicked(action, rule) {
      switch (action) {
        case "delete":
          this.onShowConfirmRuleDeletion(rule);
          break;
        case "confirm-delete":
          this.onDeleteRule(rule);
          break;
        case "select":
          this.onSelectQuery(rule);
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
    onShowConfirmRuleDeletion(id) {
      this.visibleModalId = id.query;
    },
    async onDeleteRule(rule) {
      await this.dataset.deleteLabelingRule(rule);
    },
    closeModal() {
      this.visibleModalId = undefined;
    },
  },
};
</script>
<style lang="scss" scoped>
.rules-management {
  padding-left: 4em;
  padding-top: 2em;
  margin-bottom: 2em;
  overflow: auto;
  height: 100vh;
  @extend %hide-scrollbar;
  &__header {
    display: flex;
    align-items: center;
  }
  &__title {
    @include font-size(22px);
    font-weight: 600;
    margin-top: 0;
    span {
      @include font-size(16px);
      font-weight: normal;
    }
  }
  &__button {
    margin-left: auto;
  }
  &__table {
    margin-bottom: 2em !important;
    :deep() {
      .table-info__item__col {
        width: 130px;
      }
      .table-info__item__col:first-child {
        width: auto;
        min-width: auto;
        flex-grow: 1.5;
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
}
</style>
