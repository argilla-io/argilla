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
  <results-list :dataset="dataset" v-if="!dataset.viewSettings.visibleRulesList">
    <template slot="results-header" v-if="isLabellingRules">
      <transition name="fade" mode="out-in" appear>
        {{rules}}
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
  <RulesManagementToken v-else class="content" :rules="rules" :dataset="dataset" />
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
import RulesMetricModel from "../../../models/token-classification/RulesMetric.modelTokenClassification";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      rulesHaveBeenFetched: false,
      searchQuery: "",
      ruleList: [],
    };
  },
  components: {
    RuleDefinitionToken,
  },
  async beforeMount() {},
  computed: {
    owner() {
      return this.dataset.owner;
    },
    name() {
      return this.dataset.name;
    },
    viewMode() {
      return this.dataset.viewSettings.viewMode;
    },
    isLabellingRules() {
      return this.viewMode === "labelling-rules";
    },
    datasetPrimaryKey() {
      const paramsToGetDatasetPrimaryKey = {
        name: this.name,
        owner: this.owner,
      };
      return getDatasetModelPrimaryKey(paramsToGetDatasetPrimaryKey);
    },
    queryText() {
      return (
        TokenClassificationDatasetModel.find(this.datasetPrimaryKey).query
          .text || ""
      );
    },
    rulePrimaryKey() {
      return this.getRulePrimaryKey(this.queryText);
    },
    rules() {
      return TokenClassificationDatasetModel.query()
        .whereId(this.datasetPrimaryKey)
        .with("rules")
        .first().rules
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
    async queryText(newValue, oldValue) {
      if (newValue) {
        this.rulesHaveBeenFetched = false;
        const rulesMetrics = await this.getRulesMetricsByQueryText(
          this.name,
          this.queryText
        );

        const rules = await this.fetchTokenClassificationRules(this.name);
        rules?.forEach((rule) => {
          this.insertOrUpdateDataInRuleModel(rule, rulesMetrics);
        });

        this.insertOrUpdateEntityInTokenGlobalEntityModel();
        this.rulesHaveBeenFetched = true;
      } else {
        this.cleanTables(oldValue);
      }
    },
    async selectedEntityLabel(newValue) {
      if (newValue)
        await this.addAnnotationsToRecordsByQuery(this.name, this.queryText);
    },
  },
  methods: {
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
      RuleModel.insertOrUpdate({
        data: {
          ...rule,
          rule_metrics: rulesMetrics,
          dataset_id: formatDatasetIdForTokenGlobalEntityModel(
            this.datasetPrimaryKey
          ),
          name: this.name,
          owner: this.owner,
        },
      });
    },
    insertOrUpdateEntityInTokenGlobalEntityModel() {
      const entities = [];

      this.dataset.entities.forEach(({ text, colorId }) => {
        const entity = {
          dataset_id: formatDatasetIdForTokenGlobalEntityModel(
            this.datasetPrimaryKey
          ),
          text,
          color_id: colorId,
          is_activate: false,
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
      const paramsToGetRulePrimaryKey = {
        query,
        name: this.name,
        owner: this.owner,
      };
      const rulePrimaryKey = getRuleModelPrimaryKey(paramsToGetRulePrimaryKey);
      return rulePrimaryKey;
    },
    async savingRule() {
      const ruleToPost = {
        query: this.queryText,
        label: this.selectedEntityLabel,
      };
      await this.postRule(ruleToPost);
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
    cleanTables(queryToRemove) {
      RuleAnnotationModel.deleteAll();
      EntityModel.delete(
        (entity) => entity.entitable_type === "ruleAnnotations"
      );

      const oldRulePrimaryKey = queryToRemove
        .concat(this.rulePrimaryKey)
        .split(",");
      RuleModel.delete(oldRulePrimaryKey);
      RulesMetricModel.deleteAll();
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  @extend %collapsable-if-metrics !optional;
}
</style>
