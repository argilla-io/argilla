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
    <app-header
      :dataset="dataset"
      :breadcrumbs="breadcrumbs"
      :enableSimilaritySearch="isReferenceRecord"
      @search-records="searchRecords"
    >
      <task-sidebar v-if="dataset" :dataset="dataset" />
    </app-header>
    <error
      v-if="$fetchState.error"
      link="/datasets"
      :where="datasetName"
      :error="$fetchState.error"
    ></error>
    <task-search v-else :dataset="dataset" @search-records="searchRecords" />
  </div>
</template>

<script>
import _ from "lodash";
import { mapActions, mapGetters } from "vuex";
import { currentWorkspace } from "@/models/Workspace";
import { getDatasetModelPrimaryKey } from "../../../../models/Dataset";
import { Vector as VectorModel } from "@/models/Vector";
import { RefRecord as RefRecordModel } from "@/models/RefRecord";
import { ReferenceRecord } from "@/classes/ReferenceRecord.class";
import { Base64 } from "js-base64";

export default {
  layout: "app",
  async fetch() {
    await this.fetchByName(this.datasetName);
  },
  data() {
    return {
      referenceRecord: null,
      numberOfRecords: 50,
      // isReferenceRecord: false,
    };
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
    isDataset() {
      return !_.isNil(this.dataset);
    },
    isAnyReferenceRecord() {
      return RefRecordModel.all().length;
    },
    referenceRecordId() {
      return RefRecordModel.query().first();
    },
    records() {
      if (this.isDataset) {
        return this.dataset.results?.records;
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
    areMetricsVisible() {
      return this.dataset && this.dataset.viewSettings.visibleMetrics;
    },
    annotationEnabled() {
      return this.dataset && this.dataset.viewSettings.viewMode === "annotate";
    },
    isReferenceRecord() {
      return !!RefRecordModel.all().length;
    },
  },
  mounted() {
    this.referenceRecord = ReferenceRecord;
  },
  destroyed() {
    this.referenceRecord.cleanInstance();
  },
  methods: {
    ...mapActions({
      fetchByName: "entities/datasets/fetchByName",
      search: "entities/datasets/search",
    }),
    async searchRecords(query) {
      console.log(query);
      const formattedQuery = this.formatQueryForSearch({ query });
      console.log("in index", query, formattedQuery);
      await this.search({
        dataset: this.dataset,
        ...formattedQuery,
      });
    },
    formatQueryForSearch(query) {
      let queryCloned = null;
      // this.isReferenceRecord = false;
      const isClickOnFilter = !("vector" in query);
      if (isClickOnFilter) {
        return this.initQueryWhenUserClickOnFilter(query);
      }

      queryCloned = this.initQueryWhenUserActivateRemoveSimilaritySearch(query);

      return queryCloned;
    },
    initQueryWhenUserClickOnFilter(query) {
      const vectorName = this.referenceRecord?.referenceVector?.vector_name;

      let queryForSimilaritySearch = null;
      if (!_.isNil(vectorName)) {
        // this.isReferenceRecord = true;
        const vectorValues =
          this.referenceRecord?.referenceVector?.vector_values;

        queryForSimilaritySearch = this.createQueryWithSimilaritySearch(
          vectorName,
          vectorValues
        );
      }
      const newQuery = {
        query: { ...queryForSimilaritySearch?.query, ...query.query },
      };

      return this.queryFactoryOnFilterActivation(newQuery);
    },
    initQueryWhenUserActivateRemoveSimilaritySearch(query) {
      if (!!query.vector) {
        // this.isReferenceRecord = true;
        return this.queryFactoryOnSimilaritySearchActivation(query);
      }
      this.removeReferenceRecordInstance();
      return this.queryFactoryOnFilterActivation(query);
    },
    queryFactoryOnSimilaritySearchActivation(query) {
      const { vectorId, vectorName } = query.vector;
      const vector = this.getVector(vectorId);
      const { vector_values: vectorValues } = vector;
      this.updateReferenceRecordInstance(query.recordId, vector);

      const queryForSimilaritySearch = this.createQueryWithSimilaritySearch(
        vectorName,
        vectorValues
      );

      const queryForSearch = {
        ...queryForSimilaritySearch,
        size: this.numberOfRecords,
      };
      return queryForSearch;
    },
    queryFactoryOnFilterActivation(query) {
      let queryForSimilaritySearch = {};
      if (this.isReferenceRecord) {
        const refVector = this.referenceRecord.referenceVector;
        const { vector_name: refVectorName, vector_values: refVectorValues } =
          refVector;
        queryForSimilaritySearch = this.createQueryWithSimilaritySearch(
          refVectorName,
          refVectorValues
        );
      }

      const newQuery = { ...query.query, ...queryForSimilaritySearch.query };
      return { query: newQuery, size: this.numberOfRecords };
    },
    updateReferenceRecordInstance(recordId, vector) {
      this.updateReferenceRecord(recordId);
      this.updateReferenceVector(vector);
      this.deleteAllRefRecord();
      console.log(vector);
      if (vector) {
        this.insertRefRecordInRefRecordModel(vector);
      }
      this.pushVectorIdInRouteParams(vector);
    },
    removeReferenceRecordInstance() {
      this.updateReferenceRecordInstance();
      this.deleteAllRefRecord();
    },
    updateReferenceRecord(recordId) {
      if (recordId) {
        const refRecord = this.records.find((record) => record.id === recordId);
        this.referenceRecord.setReferenceRecord(refRecord);
      } else {
        this.referenceRecord.setReferenceRecord(null);
      }
    },
    updateReferenceVector(vector = null) {
      this.referenceRecord.setReferenceVector(vector);
    },
    createQueryWithSimilaritySearch(vectorName, vectorValues) {
      const queryForSimilaritySearch = this.getQueryFactoryForSimilaritySearch(
        vectorName,
        vectorValues
      );

      const formattedQuery = {
        query: queryForSimilaritySearch,
      };
      return formattedQuery;
    },
    getQueryFactoryForSimilaritySearch(vectorName, vectorValues) {
      const queryForSimilaritySearch = {
        vector: {
          name: vectorName,
          value: vectorValues,
        },
      };
      return queryForSimilaritySearch;
    },
    insertRefRecordInRefRecordModel(refRecord) {
      RefRecordModel.insert({
        data: refRecord,
      });
    },
    deleteAllRefRecord() {
      RefRecordModel.deleteAll();
    },
    pushVectorIdInRouteParams(vector) {
      this.$router.push({
        query: {
          ...this.$route.query,
          vectorId: vector
            ? Base64.encode(
                JSON.stringify({
                  vector_name: vector.vector_name,
                  dataset_id: vector.dataset_id,
                  record_id: vector.record_id,
                })
              )
            : null,
        },
      });
    },
    getVector(vectorId) {
      console.log(vectorId);
      return VectorModel.query().whereId(vectorId).first();
    },
  },
};
</script>

<style lang="scss" scoped></style>
