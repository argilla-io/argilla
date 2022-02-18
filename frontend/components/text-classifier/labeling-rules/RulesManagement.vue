<template>
  <div v-if="isVisible" class="rules-management">
    <ReLoading v-if="$fetchState.pending" />
    <div v-else-if="!$fetchState.error">
      <rules-metrics
        title="Overall Metrics"
        :dataset="dataset"
        metrics-type="overall"
      >
        <template #button-top>
          <re-button
            class="rules-management__close button-quaternary--outline"
            @click="hideList"
          >
            <svgicon
              name="chev-left"
              color="white"
              width="12"
              height="12"
            ></svgicon
            >Back to query view</re-button
          >
        </template>
      </rules-metrics>
      <div class="rules-management__container">
        <p class="rules-management__title">
          Rules
          <span v-if="formattedRules.length"
            >({{ formattedRules.length }})</span
          >
        </p>
        <ReSearchBar
          v-if="formattedRules.length"
          placeholder="Search rule by name"
          @input="onSearch"
        />
        <ReTableInfo
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
  </div>
</template>
<script>
import "assets/icons/empty-rules";
import { mapActions } from "vuex";
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
      querySearch: undefined,
      visibleModalId: undefined,
      isLoading: undefined,
      tableColumns: [
        {
          name: "Query",
          field: "query",
          class: "table-info__title",
          type: "action",
        },
        { name: "Label", field: "label", class: "text" },
        {
          name: "Coverage",
          field: "coverage",
          class: "text",
          type: "percentage",
          tooltip: "Percentage of records labeled by the rule",
        },
        {
          name: "Annot. Cover.",
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
            "Number of records the rule labeled correctly (if annotations are available)",
        },
        {
          name: "Incorrect",
          field: "incorrect",
          class: "text",
          tooltip:
            "Number of records the rule labeled incorrectly (if annotations are available)",
        },
        {
          name: "Precision",
          field: "precision",
          class: "text",
          type: "percentage",
          tooltip: "Percentage of correct labels given by the rule",
        },
        {
          name: "Created at",
          field: "created_at",
          class: "date",
          type: "date",
        },
      ],
      sortedOrder: "desc",
      sortedByField: "created_at",
      actions: [{ name: "delete", icon: "delete", title: "Delete rule" }],
      noDataInfo: {
        title: "0 rules defined",
        message: `You have not defined any rules for this dataset yet.`,
        icon: "empty-rules",
      },
      emptySearchInfo: {
        title: "0 rules found",
      },
    };
  },
  async fetch() {
    if (!this.rules) {
      await this.dataset.refreshRules();
    }
  },
  computed: {
    rules() {
      return this.dataset.labelingRules;
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
            label: r.label,
            ...this.metricsForRule(r),
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

    metricsForRule(rule) {
      const metrics = this.perRuleMetrics[rule.query];
      if (!metrics) {
        return {};
      }
      return {
        coverage: metrics.coverage,
        coverage_annotated: metrics.coverage_annotated,
        correct: metrics.correct,
        incorrect: metrics.incorrect,
        precision: !isNaN(metrics.precision) ? metrics.precision : "-",
      };
    },

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
  padding-top: 7em;
  overflow: auto;
  height: 100vh;
  &__container {
    padding: 20px;
    background: rgba($lighter-color, 0.4);
    border: 1px solid $lighter-color;
    width: 100%;
    border-radius: 5px;
  }
  &__title {
    color: $font-secondary-dark;
    @include font-size(22px);
    font-weight: 600;
    margin-top: 0;
    span {
      @include font-size(16px);
      font-weight: normal;
    }
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
    position: absolute;
    right: 30px;
    top: 30px;
  }
}
.rule-metrics {
  &__container {
    width: 100%;
    margin-left: 0 !important;
    margin-bottom: 20px;
    min-height: 180px;
    &::v-deep {
      .rule-metrics {
        display: flex;
        &__item {
          width: 100%;
          margin-top: 1em;
        }
      }
    }
  }
}
</style>
