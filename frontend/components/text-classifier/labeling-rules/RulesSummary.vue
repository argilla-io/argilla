<template>
  <div v-if="isVisible">
    <ReLoading v-if="$fetchState.pending" />
    <div v-else-if="!$fetchState.error" class="rules-summary__container">
      <re-button @click="hideList()" class="rules-summary__close button-quaternary">
        <svgicon
          name="chev-left"
          width="12"
          height="12"
        ></svgicon>Back to query view</re-button>
      <p class="rules-summary__title">Summary</p>
      <rules-summary-metrics v-if="formattedRules.length" :metricsByLabel="metricsByLabel" :dataset="dataset" /> 
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
        :show-modal="showModal"
        @sort-column="onSortColumns"
        @onActionClicked="onActionClicked"
        @close-modal="closeModal"
      />
      <re-button class="button-primary" @click="updateSummary()">Update Summary</re-button>
    </div>
  </div>
</template>
<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
export default {
  props: {
    dataset: {
      type: Object,
      default: () => ({})
    }
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
        { name: "Cov. Annot.", field: "coverage_annotated", class: "text", type: "number" },
        { name: "Correct", field: "correct", class: "text" },
        { name: "Incorrect", field: "incorrect", class: "text" },
        { name: "Precision", field: "precision", class: "text", type: "number"  },
      ],
      sortedOrder: "desc",
      sortedByField: "query",
      actions: [{ name: "delete", icon: "delete", title: "Delete dataset" }]
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
      return this.rules.map(r => {
        return {
          name: r.description,
          kind: "select",
          label: r.label,
          coverage: this.metricsByLabel[r.query].coverage,
          coverage_annotated: this.metricsByLabel[r.query].coverage_annotated,
          correct: this.metricsByLabel[r.query].correct,
          incorrect: this.metricsByLabel[r.query].incorrect,
          precision: this.metricsByLabel[r.query].precision,
        };
      });
    }
  },
  mounted() {
    document.getElementsByTagName("body")[0].classList.remove("fixed-header");
  },
  methods: {
    ...mapActions({
      search: "entities/datasets/search",
      getRules: "entities/text_classification/getRules",
      deleteRule: "entities/text_classification/deleteRule",
      getRuleMetricsByLabel: "entities/text_classification/getRuleMetricsByLabel",
    }),
    async hideList() {
      await DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          visibleRulesList: false
        }
      });
    },
    async getMetricsByLabel() {
      for(let rule of this.rules) {
        const response = await this.getRuleMetricsByLabel({
          dataset: this.dataset,
          query: rule.query,
          label: rule.label,
        })
        this.metricsByLabel[rule.query] = response;
      }
    },
    async onSelectQuery(id) {
      if (id !== this.dataset.query.text) {
        await this.search({ dataset: this.dataset, query: { text: id } });
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
          this.onSelectQuery(rowId)
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
    updateSummary() {
      this.getMetricsByLabel();
    },
    onShowConfirmRuleDeletion(id) {
      this.showModal = id.name;
    },
    async onDeleteRule(id) {
      await this.deleteRule({ 
        dataset: this.dataset,
        query: id.name,
      });
      await this.$fetch();
      this.closeModal();
    },
    closeModal() {
      this.showModal = undefined;
    }
  }
};
</script>
<style lang="scss" scoped>
.rules-summary {
  &__container {
    margin-top: 3em;
    padding: 3em;
  }
  &__title {
    color: $font-secondary-dark;
    @include font-size(22px);
    font-weight: 600;
  }
  &__table {
    ::v-deep {
      .table-info__item__col:nth-of-type(2) {
        min-width: 100px;
      }
      .table-info__item__col:first-child {
        min-width: 120px;
      }
      .table-info__body {
        height: calc(100vh - 503px);
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

