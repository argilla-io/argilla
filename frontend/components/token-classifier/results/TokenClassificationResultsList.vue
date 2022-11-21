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
  <results-list :dataset="dataset" v-if="isViewRuleDefinitionOrRecords">
    <template slot="results-header" v-if="isViewWeakLabelling">
      <transition name="fade" mode="out-in" appear>
        <RuleDefinitionToken
          :rule="rule"
          :queryText="queryText"
          :entities="globalEntities"
          :numberOfRecords="numberOfRecords"
          @on-search-entity="(value) => (searchQuery = value)"
          @on-saving-rule="savingRule"
        />
      </transition>
    </template>
    <template slot="record" slot-scope="results">
      <record-token-classification
        :dataset="dataset"
        :record="results.record"
      />
    </template>
  </results-list>
  <RulesManagementToken
    v-else
    class="content"
    :rules="rulesSavedInDataset"
    :dataset="dataset"
  />
</template>

<script>
import {
  Rule as RuleModel,
  getRuleModelPrimaryKey,
} from "../../../models/token-classification/Rule.modelTokenClassification";
import { TokenClassificationDataset as TokenClassificationDatasetModel } from "../../../models/TokenClassification";
import RuleDefinitionToken from "../labelling-rules/RuleDefinitionToken.component.vue";
import { getDatasetModelPrimaryKey } from "../../../models/Dataset";
import {
  formatDatasetIdForTokenGlobalEntityModel,
  TokenGlobalEntity as GlobalEntityModel,
} from "../../../models/token-classification/TokenGlobalEntity.modelTokenClassification";
import { TokenEntity as EntityModel } from "../../../models/token-classification/TokenEntity.modelTokenClassification";
import { formatAnnotationPredictionid } from "../../../models/token-classification/TokenRecord.modelTokenClassification";
import {
  formatEntityIdForRuleAnnotation,
  TokenRuleAnnotation as RuleAnnotationModel,
} from "../../../models/token-classification/TokenRuleAnnotation.modelTokenClassification";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      searchQuery: "",
      ruleList: [],
    };
  },
  components: {
    RuleDefinitionToken,
  },
  computed: {
    owner() {
      return this.dataset.owner;
    },
    name() {
      return this.dataset.name;
    },
    viewSettings() {
      return TokenClassificationDatasetModel.query()
        .whereId(this.datasetPrimaryKey)
        .with("viewSettings")
        .first().viewSettings;
    },
    viewMode() {
      return this.viewSettings.viewMode;
    },
    isViewWeakLabelling() {
      return this.viewMode === "labelling-rules";
    },
    datasetPrimaryKey() {
      const paramsToGetDatasetPrimaryKey = {
        name: this.name,
        owner: this.owner,
      };
      return getDatasetModelPrimaryKey(paramsToGetDatasetPrimaryKey);
    },
    joinedDatasetPrimaryKey() {
      return this.datasetPrimaryKey.join(".");
    },
    isViewRuleDefinitionOrRecords() {
      // NOTE: IF true => the view is rule_management ELSE the view is rule_definition or record_view
      return !this.viewSettings.visibleRulesList;
    },
    queryText() {
      return (
        TokenClassificationDatasetModel.find(this.datasetPrimaryKey).query
          .text || ""
      );
    },
    isRuleForCurrentQuery() {
      const ruleModelPrimaryKeyWithCurrentQuery = getRuleModelPrimaryKey({
        query: this.queryText,
        name: this.name,
        owner: this.owner,
      });
      return RuleModel.query()
        .whereId(ruleModelPrimaryKeyWithCurrentQuery)
        .exists();
    },
    rulePrimaryKey() {
      return this.getRulePrimaryKey(this.queryText);
    },
    rulesSavedInDataset() {
      return RuleModel.query()
        .with("rule_metrics")
        .where("dataset_id", this.joinedDatasetPrimaryKey)
        .where("is_saved_in_dataset", true)
        .get();
    },
    rules() {
      return TokenClassificationDatasetModel.query()
        .whereId(this.datasetPrimaryKey)
        .with("rules")
        .first().rules;
    },
    isRulesInDataset() {
      return this.rules.length;
    },
    isViewIsWeakLabellingANDDatasetHaveNoRules() {
      return this.isViewWeakLabelling && !this.isRulesInDataset;
    },
    rule() {
      return (
        RuleModel.query()
          .with("rule_metrics")
          .whereId(this.rulePrimaryKey)
          .first() || {}
      );
    },
    globalEntities() {
      return GlobalEntityModel.query()
        .where(
          "dataset_id",
          formatDatasetIdForTokenGlobalEntityModel(this.datasetPrimaryKey)
        )
        .where("text", (value) =>
          this.isStringIncludeSubstring(value, this.searchQuery)
        )
        .orderBy("text")
        .get();
    },
    selectedEntityLabel() {
      return GlobalEntityModel.query().where("is_activate", true).first()?.text;
    },
    records() {
      return TokenClassificationDatasetModel.query()
        .whereId(this.datasetPrimaryKey)
        .with("token_records.token_annotation")
        .first().token_records;
    },
    entities() {
      return EntityModel.query().with("token_entitable").get();
    },
    recordsIds() {
      return this.records.map((record) => record.id);
    },
    numberOfRecords() {
      return (
        this.rule.rule_metrics?.coverage *
          this.rule.rule_metrics?.total_records || null
      );
    },
  },
  watch: {
    async isViewWeakLabelling() {
      if (this.isViewIsWeakLabellingANDDatasetHaveNoRules) {
        this.initRuleModelAndRulesMetricsModel();
      }
    },
    async queryText(newValue, oldValue) {
      if (newValue) {
        if (!this.isRuleForCurrentQuery) {
          this.createACustomRuleAndLoadRuleMetrics();
        } else {
          // NOTE: we do nothing because we already have the rules and it rule_metrics
        }
        this.insertOrUpdateEntityInTokenGlobalEntityModel();
      } else {
        this.cleanTables();
      }
    },
    async selectedEntityLabel(newValue) {
      if (newValue)
        await this.addAnnotationsToRecordsByQuery(this.name, this.queryText);
    },
  },
  methods: {
    async initRuleModelAndRulesMetricsModel() {
      const rules = await this.fetchTokenClassificationRules(this.name);
      rules?.forEach(async (rule) => {
        const rulesMetrics = await this.getRulesMetricsByQueryText(
          this.name,
          rule.query
        );
        this.insertOrUpdateDataInRuleModel(rule, rulesMetrics);
      });
    },
    async getRulesMetricsByQueryText(name, query) {
      let rulesMetrics = null;

      if (query) {
        rulesMetrics = await this.fetchRuleMetricsByQueryText(name, query);
      }
      return rulesMetrics;
    },
    async fetchTokenClassificationRules(name) {
      try {
        const { data, status } = await this.$axios.get(
          `/datasets/${name}/TokenClassification/labeling/rules`
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
    async fetchRuleMetricsByQueryText(name, query) {
      try {
        const { data, status } = await this.$axios.get(
          `/datasets/${name}/TokenClassification/labeling/rules/${query}/summary`
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
    async addAnnotationsToRecordsByQuery(name, query) {
      const data = query
        ? await this.fetchRecordsAnnotationByQueryText(name, query)
        : null;

      if (data) {
        this.insertOrUpdateRuleAnnotations(data);
      }
    },
    async fetchRecordsAnnotationByQueryText(name, query) {
      try {
        const { data, status } = await this.$axios.post(
          `/datasets/${name}/TokenClassification/labeling/rules/${query}/search?label=${this.selectedEntityLabel}`,
          {
            record_ids: this.recordsIds,
          }
        );
        if (status === 200) {
          return data;
        } else {
          throw new Error("Error fetching API records annotations");
        }
      } catch (error) {
        console.log("Error: ", error);
      }
    },
    insertOrUpdateDataInRuleModel(rule, rulesMetrics) {
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
        name: this.name,
        owner: this.owner,
      };
      RuleModel.insertOrUpdate({
        data: newRule,
      });
    },
    insertOrUpdateEntityInTokenGlobalEntityModel() {
      const entities = [];

      this.dataset.entities.forEach(({ text, colorId }) => {
        const isActivate = text === this.rule.label || false;
        const entity = {
          dataset_id: formatDatasetIdForTokenGlobalEntityModel(
            this.datasetPrimaryKey
          ),
          text,
          color_id: colorId,
          is_activate: isActivate,
        };

        entities.push(entity);
      });

      TokenClassificationDatasetModel.insertOrUpdate({
        where: this.datasetPrimaryKey,
        data: {
          token_global_entities: entities,
        },
      });
    },
    insertOrUpdateRuleAnnotations({ agent, records }) {
      records.forEach(({ id: record_id, entities }, index) => {
        const tokenRuleAnnotation = this.initRuleAnnotationObj(
          record_id,
          entities,
          agent,
          index
        );
        RuleAnnotationModel.insertOrUpdate({ data: tokenRuleAnnotation });
      });
    },
    initRuleAnnotationObj(record_id, entities, agent, prefix) {
      const tokenEntities = entities.map(({ label, start, end }) => {
        const idPrefix = `${record_id}_${start}_${end}`;
        return {
          id: formatEntityIdForRuleAnnotation(idPrefix),
          record_id,
          agent,
          label,
          start,
          end,
        };
      });

      const tokenRuleAnnotation = {
        id: formatAnnotationPredictionid(prefix, this.datasetPrimaryKey),
        query_search: agent,
        record_id,
        token_entities: tokenEntities,
      };
      return tokenRuleAnnotation;
    },
    isStringIncludeSubstring(refString, substring) {
      return refString.toLowerCase().includes(substring.toLowerCase());
    },
    getRulePrimaryKey(query) {
      const paramsToGetRulePrimaryKey = this.initRulePrimaryKey(query);
      const rulePrimaryKey = getRuleModelPrimaryKey(paramsToGetRulePrimaryKey);
      return rulePrimaryKey;
    },
    async savingRule() {
      if (this.rule.is_saved_in_dataset) {
        await this.updateRule(this.queryText, this.selectedEntityLabel);
      } else {
        const ruleToPost = {
          query: this.queryText,
          label: this.selectedEntityLabel,
        };
        await this.postRule(ruleToPost);
      }
    },
    async postRule(ruleToPost) {
      try {
        const { data, status } = await this.$axios.post(
          `/datasets/${this.name}/TokenClassification/labeling/rules`,
          ruleToPost
        );
        if (status === 200) {
          return data;
        } else if (status === 409) {
          throw new Error("Error posting API rule because it already exist");
        } else {
          throw new Error("Error posting API rule");
        }
      } catch (error) {
        console.log("Error: ", error);
      }
    },
    async updateRule(query, label) {
      try {
        const { data, status } = await this.$axios.patch(
          `/datasets/${this.name}/TokenClassification/labeling/rules/${query}`,
          { label }
        );
        if (status === 200) {
          return data;
        } else {
          throw new Error("Error update API rule");
        }
      } catch (error) {
        console.log("Error: ", error);
      }
    },
    initRulePrimaryKey(query) {
      return {
        query,
        name: this.name,
        owner: this.owner,
      };
    },
    async createACustomRuleAndLoadRuleMetrics() {
      const rulesMetrics = await this.getRulesMetricsByQueryText(
        this.name,
        this.queryText
      );

      const paramsToGetRulePrimaryKey = this.initRulePrimaryKey(this.queryText);
      const rulePrimaryKey = getRuleModelPrimaryKey(paramsToGetRulePrimaryKey);
      const newRule = {
        is_saved_in_dataset: false,
        dataset_id: this.joinedDatasetPrimaryKey,
        label: null,
        labeling_function: null,
        name: this.name,
        owner: this.owner,
        query: paramsToGetRulePrimaryKey.query,
        rule_metrics: {
          ...rulesMetrics,
          query: paramsToGetRulePrimaryKey.query,
          dataset_id: this.joinedDatasetPrimaryKey,
        },
      };

      RuleModel.insertOrUpdate({ where: rulePrimaryKey, data: newRule });
    },
    cleanTables() {
      RuleAnnotationModel.deleteAll();
      EntityModel.delete(
        (entity) => entity.entitable_type === "ruleAnnotations"
      );

      RuleModel.delete((rule) => {
        return !rule.is_saved_in_dataset;
      });
      // this.rules.forEach((rule) => {
      //   RulesMetricModel.delete((metric) => {
      //     return metric.query === rule.query;
      //   });
      // });
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  @extend %collapsable-if-metrics !optional;
}
</style>
