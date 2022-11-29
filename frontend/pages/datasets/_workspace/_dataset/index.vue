<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <base-loading v-if="$fetchState.pending" />
  <div
    :class="[
      'app',
      annotationEnabled ? '--annotation' : '',
      areMetricsVisible ? '--metrics' : '',
    ]"
    v-else
  >
    <app-header :dataset="dataset" :breadcrumbs="breadcrumbs">
      <task-sidebar v-if="dataset" :dataset="dataset" />
    </app-header>
    <error
      v-if="$fetchState.error"
      link="/datasets"
      :where="datasetName"
      :error="$fetchState.error"
    ></error>
    <task-search v-else :dataset="dataset" />
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { currentWorkspace } from "@/models/Workspace";
import { formatDatasetIdForTokenGlobalEntityModel } from "../../../../models/token-classification/TokenGlobalEntity.modelTokenClassification";
import { Rule as RuleModel } from "../../../../models/token-classification/Rule.modelTokenClassification";
import { getDatasetModelPrimaryKey } from "../../../../models/Dataset";

export default {
  layout: "app",
  async fetch() {
    await this.fetchByName(this.datasetName);
    if (this.datasetTask === "TokenClassification") {
      await this.initRuleModelAndRulesMetricsModel();
    }
  },
  computed: {
    ...mapGetters({
      findByName: "entities/datasets/findByName",
    }),
    breadcrumbs() {
      return [
        { link: { path: "/datasets" }, name: "Datasets" },
        {
          link: { path: `/datasets?workspace=${this.workspace}` },
          name: this.workspace,
        },
        {
          link: this.$route.fullPath,
          name: this.dataset ? this.dataset.name : undefined,
        },
      ];
    },
    dataset() {
      // This computed data makes that store updates could be shown here
      try {
        return this.findByName(this.datasetName);
      } catch {
        return null;
      }
    },
    datasetName() {
      return this.$route.params.dataset;
    },
    workspace() {
      return currentWorkspace(this.$route);
    },
    datasetPrimaryKey() {
      const paramsToGetDatasetPrimaryKey = {
        name: this.datasetName,
        owner: this.workspace,
      };
      return getDatasetModelPrimaryKey(paramsToGetDatasetPrimaryKey);
    },
    datasetTask() {
      switch (this.dataset.task.toLowerCase()) {
        case "tokenclassification":
          return "TokenClassification";
        default:
          return null;
      }
    },
    areMetricsVisible() {
      return this.dataset && this.dataset.viewSettings.visibleMetrics;
    },
    annotationEnabled() {
      return this.dataset && this.dataset.viewSettings.viewMode === "annotate";
    },
  },
  methods: {
    ...mapActions({
      fetchByName: "entities/datasets/fetchByName",
    }),
    async initRuleModelAndRulesMetricsModel() {
      const rules = await this.fetchTokenClassificationRules(this.datasetName);
      rules?.forEach(async (rule) => {
        const rulesMetrics = await this.getRulesMetricsByQueryText(
          this.datasetName,
          rule.query
        );
        await this.insertOrUpdateDataInRuleModel(rule, rulesMetrics);
      });
    },
    async fetchTokenClassificationRules(name) {
      try {
        const { data, status } = await this.$axios.get(
          `/datasets/${name}/${this.datasetTask}/labeling/rules`
        );
        if (status === 200) {
          return data;
        } else {
          throw new Error("Error fetching API rules");
        }
      } catch (error) {
        console.log("Error: ", error);
      }
    },
    async getRulesMetricsByQueryText(name, query) {
      // FIXME: duplication of code with TokenClassificationResultsList => function needs to be externalized
      let rulesMetrics = null;

      if (query) {
        rulesMetrics = await this.fetchRuleMetricsByQueryText(name, query);
      }
      return rulesMetrics;
    },
    async fetchRuleMetricsByQueryText(name, query) {
      try {
        const { data, status } = await this.$axios.get(
          `/datasets/${name}/${this.datasetTask}/labeling/rules/${query}/summary`
        );
        if (status === 200) {
          return data;
        } else {
          throw new Error("Error fetching API rule metrics");
        }
      } catch (error) {
        console.log("Error: ", error);
      }
    },
    async insertOrUpdateDataInRuleModel(rule, rulesMetrics) {
      const datasetId = formatDatasetIdForTokenGlobalEntityModel(
        this.datasetPrimaryKey
      );
      const newRule = {
        ...rule,
        rule_metrics: {
          ...rulesMetrics,
          query: rule.query,
          dataset_id: datasetId,
        },
        dataset_id: datasetId,
        name: this.datasetName,
        owner: this.workspace,
      };
      await RuleModel.insertOrUpdate({
        data: newRule,
      });
    },
  },
};
</script>

<style lang="scss" scoped></style>
