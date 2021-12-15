<template>
  <div v-if="isVisible">
    <ReLoading v-if="$fetchState.pending" />
    <div v-else-if="!$fetchState.error" class="rules__list__container">
      <re-button @click="hideList()" class="rules__list__close primary-color">Back to query view</re-button>
      <p class="rules__list__title">Summary</p>
      <ReSearchBar @input="onSearch" />
      <ReTableInfo
        class="rules__list__table"
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
      test: undefined,
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
          correct: this.metricsByLabel[r.query].correct,
          incorrect: this.metricsByLabel[r.query].incorrect,
          precision: this.metricsByLabel[r.query].precision,
        };
      });
    }
  },
  methods: {
    ...mapActions({
      search: "entities/datasets/search",
      getRules: "entities/datasets/getRules",
      deleteRule: "entities/datasets/deleteRule",
      getRuleMetrics: "entities/datasets/getRuleMetrics",
      getRuleMetricsByLabel: "entities/datasets/getRuleMetricsByLabel",
    }),
    async hideList() {
      await DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          visibleRulesList: false
        }
      });
    },
    // async getMetrics() {
    //   for(let rule of this.rules) {
    //     const response = await this.getRuleMetrics({
    //       dataset: this.dataset,
    //       query: rule.query,
    //     })
    //     this.test = response;
    //   }
    // },
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
      this.showModal = id;
    },
    async onDeleteRule(id) {
      await this.deleteRule({ 
        dataset: this.dataset,
        query: id,
      });
      this.closeModal();
      this.$fetch();
    },
    closeModal() {
      this.showModal = undefined;
    }
  }
};
</script>
<style lang="scss" scoped>
.rules__list {
  &__container {
    margin-top: 3em;
    padding: 3em;
  }
  &__title {
    color: $font-secondary-dark;
    @include font-size(22px);
  }
  &__table {
    ::v-deep {
      .table-info__item__col:nth-of-type(2) {
        min-width: 140px;
      }
      .table-info__item__col:first-child {
        min-width: 180px;
      }
      .table-info__body {
        height: auto;
      }
    }
  }
  &__close {
    float: right;
  }
}
</style>

