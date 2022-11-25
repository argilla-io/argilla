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
          :isGlobalEntities="isGlobalEntities"
          :filteredEntities="filteredGlobalEntities"
          :numberOfRecords="numberOfRecords"
          :numberOfRulesInDataset="numberOfRulesInDataset"
          :isSaveRulesBtnDisabled="isSaveRulesBtnDisabled"
          :isCancelBtnDisabled="isCancelBtnDisabled"
          :ruleStatus="ruleStatus"
          @on-search-entity="(value) => (searchEntity = value)"
          @on-select-global-entity="updateSelectedEntity"
          @on-saving-rule="savingRule"
          @on-click-view-rules="goToManageRules"
          @on-click-go-to-annotation-mode="goToAnnotationMode"
          @on-click-cancel="clickOnCancel"
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
  <rules-management-token
    v-else
    class="content"
    :rules="rulesSavedInDataset"
    :dataset="dataset"
    @on-click-delete-rule="deleteRule"
  />
</template>

<script>
import _ from "lodash";
import { mapActions } from "vuex";
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
import DatasetViewSettings from "../../../models/DatasetViewSettings";
import { PROPERTIES } from "../labelling-rules/labellingRules.properties";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      searchEntity: "",
      initialGlobalEntities: [],
      initialSelectedEntity: null,
      selectedGlobalEntity: null,
      ruleIsSaved: false,
      RULE_STATUS: PROPERTIES.RULE_STATUS,
    };
  },
  async mounted() {
    await this.initRuleModelAndRulesMetricsModel();
    this.initialGlobalEntities = this.initGlobalEntities();
  },
  components: {
    RuleDefinitionToken,
  },
  computed: {
    filteredGlobalEntities() {
      return structuredClone(
        this.initialGlobalEntities.filter((globalEntity) => {
          return globalEntity.text
            .toUpperCase()
            .includes(this.searchEntity.toUpperCase());
        })
      );
    },
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
    isViewRuleDefinitionOrRecords() {
      // NOTE: IF true => the view is rule_management ELSE the view is rule_definition or record_view
      return !this.viewSettings.visibleRulesList;
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
      return (
        RuleModel.query()
          .with("rule_metrics")
          .where("dataset_id", this.joinedDatasetPrimaryKey)
          .where("is_saved_in_dataset", true)
          .get() || []
      );
    },
    numberOfRulesInDataset() {
      return this.rulesSavedInDataset.length;
    },
    rules() {
      return TokenClassificationDatasetModel.query()
        .whereId(this.datasetPrimaryKey)
        .with("rules")
        .first().rules;
    },
    rule() {
      return (
        RuleModel.query()
          .with("rule_metrics")
          .whereId(this.rulePrimaryKey)
          .first() || {}
      );
    },
    isSelectedGlobalEntity() {
      return !_.isNil(this.selectedGlobalEntity);
    },
    isinitialSelectedGlobalEntity() {
      return !_.isNil(this.initialSelectedEntity);
    },
    isNoInitialSelectedEntityAndNoSelectedGlobalEntity() {
      return (
        !this.isinitialSelectedGlobalEntity && !this.isSelectedGlobalEntity
      );
    },
    isNoInitialSelectedEntityAndIsSelectedGlobalEntity() {
      return !this.isinitialSelectedGlobalEntity && this.isSelectedGlobalEntity;
    },
    isInitialSelectedEntityAndIsNoSelectedGlobalEntity() {
      return this.isinitialSelectedGlobalEntity && !this.isSelectedGlobalEntity;
    },
    isInitialSelectedEntityAndIsSelectedGlobalEntity() {
      return this.isinitialSelectedGlobalEntity && this.isSelectedGlobalEntity;
    },

    isSaveRulesBtnDisabled() {
      if (this.isNoInitialSelectedEntityAndNoSelectedGlobalEntity) {
        return true;
      }
      if (this.isNoInitialSelectedEntityAndIsSelectedGlobalEntity) {
        return false;
      }
      if (this.isInitialSelectedEntityAndIsNoSelectedGlobalEntity) {
        return true;
      }
      if (this.isInitialSelectedEntityAndIsSelectedGlobalEntity) {
        if (
          this.initialSelectedEntity.text === this.selectedGlobalEntity.text
        ) {
          return true;
        }
      }
      return false;
    },
    isCancelBtnDisabled() {
      return !this.isSelectedGlobalEntity;
    },
    isGlobalEntities() {
      return this.initialGlobalEntities.length > 0;
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
    ruleStatus() {
      if (
        this.isinitialSelectedGlobalEntity &&
        this.initialSelectedEntity.text ===
          (this.selectedGlobalEntity?.text || this.initialSelectedEntity.text)
      ) {
        if (this.ruleIsSaved) {
          return this.RULE_STATUS.IS_SAVED;
        }
        return this.RULE_STATUS.ALREADY_SAVED;
      }
      return null;
    },
  },
  watch: {
    async queryText(newValue) {
      this.initSelectedEntitiesVariables();
      if (newValue.length > 0) {
        if (!this.isRuleForCurrentQuery) {
          this.initialGlobalEntities = GlobalEntityModel.query()
            .where(
              "dataset_id",
              formatDatasetIdForTokenGlobalEntityModel(this.datasetPrimaryKey)
            )
            .orderBy("text")
            .get();
          this.createACustomRuleAndLoadRuleMetrics();
        } else {
          this.updateGlobalEntitiesByRule(this.rule.label);
        }
      } else {
        // this.cleanTables();
      }
    },
    async selectedGlobalEntity(newValue) {
      if (newValue) {
        await this.addAnnotationsToRecordsByQuery(this.name, this.queryText);
      }
    },
  },
  methods: {
    ...mapActions({
      changeViewMode: "entities/datasets/changeViewMode",
    }),
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
          `/datasets/${name}/TokenClassification/labeling/rules/${query}/search?label=${this.selectedGlobalEntity.text}`,
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
    updateGlobalEntitiesByRule(label) {
      this.initialGlobalEntities = this.initialGlobalEntities.map(
        (globalEntity) => {
          if (globalEntity.text === label) {
            return { ...globalEntity, is_activate: true };
          } else {
            return { ...globalEntity, is_activate: false };
          }
        }
      );
      this.initialSelectedEntity =
        this.initialGlobalEntities.find(
          (globalEntity) => globalEntity.is_activate
        ) || null;
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
      let response = null;
      if (this.rule.is_saved_in_dataset) {
        response = await this.updateRule(
          this.queryText,
          this.selectedGlobalEntity.text
        );
      } else {
        const ruleToPost = {
          query: this.queryText,
          label: this.selectedGlobalEntity.text,
        };
        response = await this.postRule(ruleToPost);
      }

      if (response) {
        this.ruleIsSaved = true;
        this.updateGlobalEntitiesByRule(this.selectedGlobalEntity.text);
        const { author, created_at } = response;
        this.updateRuleModel(
          this.selectedGlobalEntity.text,
          author,
          created_at
        );
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
    async deleteRule(query) {
      await this.dataset.deleteLabelingRule(query);
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
    goToManageRules() {
      DatasetViewSettings.update({
        where: getDatasetModelPrimaryKey,
        data: {
          visibleRulesList: true,
        },
      });
    },
    goToAnnotationMode() {
      this.changeViewMode({
        dataset: this.dataset,
        value: "annotate",
      });
    },
    updateSelectedEntity(id) {
      this.initialGlobalEntities = this.initialGlobalEntities.map(
        (globalEntity) => {
          if (globalEntity.id === id) {
            const selectedGlobalEntity = {
              ...globalEntity,
              is_activate: true,
            };
            this.selectedGlobalEntity = selectedGlobalEntity;
            return selectedGlobalEntity;
          }
          return { ...globalEntity, is_activate: false };
        }
      );
    },
    updateRuleModel(label, author, created_at) {
      RuleModel.update({
        where: this.rulePrimaryKey,
        data: {
          is_saved_in_dataset: true,
          created_at,
          author,
          label,
        },
      });
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
    clickOnCancel() {
      this.initialGlobalEntities = this.initGlobalEntities();
      this.selectedGlobalEntity = this.initialSelectedEntity;
    },
    initGlobalEntities() {
      let initialGlobalEntities = GlobalEntityModel.query()
        .where(
          "dataset_id",
          formatDatasetIdForTokenGlobalEntityModel(this.datasetPrimaryKey)
        )
        .orderBy("text")
        .get();
      initialGlobalEntities = initialGlobalEntities.map((globalEntity) => {
        if (globalEntity.id === this.initialSelectedEntity?.id) {
          return {
            ...globalEntity,
            is_activate: true,
          };
        }
        return {
          ...globalEntity,
          is_activate: false,
        };
      });
      return initialGlobalEntities;
    },
    initSelectedEntitiesVariables() {
      this.ruleIsSaved = false;
      this.initialSelectedEntity = null;
      this.selectedGlobalEntity = null;
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  @extend %collapsable-if-metrics !optional;
}
</style>
