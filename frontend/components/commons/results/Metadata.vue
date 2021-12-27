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
  <div class="metadata">
    <div v-if="typeof title === 'object'">
      <p
        v-for="name in title"
        :key="name.index"
        class="metadata__title"
        :title="name"
      >
        <span v-if="!Array.isArray(name)">{{ name | truncate(100) }}</span>
      </p>
    </div>
    <div v-else>
      <p class="metadata__title">{{ title }}</p>
    </div>
    <div class="metadata__container">
      <div v-for="(item, index) in formatSortedMetadataItems" :key="index">
        <div class="metadata__blocks">
          <ReCheckbox
            :id="item[0]"
            v-model="selectedMetadata"
            class="re-checkbox--dark"
            :value="item[0]"
          >
            <div class="metadata__key">
              {{ item[0] }}
              <div class="metadata__value">
                {{ item[1] }}
              </div>
            </div>
          </ReCheckbox>
        </div>
      </div>
    </div>
    <div class="metadata__buttons">
      <ReButton
        class="button-tertiary--small button-tertiary--outline"
        @click="$emit('cancel')"
      >
        Cancel
      </ReButton>
      <ReButton class="button-primary--small" @click="applySelectedFilters()">
        Filter
      </ReButton>
    </div>
  </div>
</template>

<script>
export default {
  filters: {
    truncate(string, value) {
      if (string.length > value) {
        return `${string.substring(0, value)}...`;
      }
      return string;
    },
  },
  props: {
    metadataItems: {
      type: Object,
      required: true,
    },
    appliedFilters: {
      type: Object,
      default: () => {},
    },
    title: {
      type: [Object, String],
      required: true,
    },
  },
  data: () => ({
    selectedMetadata: [],
  }),
  computed: {
    normalizedMetadataItems() {
      return Object.keys(this.metadataItems).reduce(
        (r, k) => ((r[k] = String(this.metadataItems[k])), r),
        {}
      );
    },
    sortedMetadataItems() {
      return Object.keys(this.normalizedMetadataItems)
        .sort()
        .reduce((r, k) => ((r[k] = this.normalizedMetadataItems[k]), r), {});
    },
    formatSortedMetadataItems() {
      return Object.entries(this.sortedMetadataItems);
    },
  },
  mounted() {
    if (this.appliedFilters) {
      Object.keys(this.appliedFilters).map((key) => {
        if (
          this.appliedFilters[key].includes(this.normalizedMetadataItems[key])
        ) {
          this.selectedMetadata.push(key);
        }
      });
    }
  },
  methods: {
    applySelectedFilters() {
      const filters = Object.keys(this.appliedFilters || {}).reduce(
        (r, k) => (
          (r[k] = Array.isArray(this.appliedFilters[k])
            ? this.appliedFilters[k].filter(
                (v) => v !== this.normalizedMetadataItems[k]
              )
            : []),
          r
        ),
        {}
      );

      this.selectedMetadata.map((key) => {
        filters[key] = this.normalizedMetadataItems[key];
      });

      this.$emit("metafilterApply", filters);
    },
    isApplied(item) {
      if (this.appliedFilters) {
        return Object.keys(this.appliedFilters).includes(item[0]);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.metadata {
  position: relative;
  max-width: 500px;
  margin: auto;
  pointer-events: all;
  &__title {
    color: $font-dark-color;
    font-weight: 600;
    margin-top: 2em;
    margin-right: 2em;
    white-space: pre-line;
    display: none;
    &:first-child {
      margin-top: 0;
    }
    &:nth-child(-n + 5) {
      display: block;
    }
  }
  &__container {
    max-height: 50vh;
    overflow-y: auto;
    margin-right: -1em;
    padding-right: 1em;
  }
  &__blocks {
    display: flex;
    align-items: center;
    .re-checkbox--dark {
      width: 100%;
      display: flex;
      align-items: center;
      margin-right: 0;
    }
    ::v-deep .checkbox-label {
      height: auto !important;
    }
  }
  &__block {
    padding: 1em 0;
    margin-right: 0.5em;
    color: $font-dark-color;
    font-weight: 600;
    &__item {
      word-break: break-word;
      min-width: 200px;
      max-width: 300px;
      text-align: left;
      white-space: pre-line;
      color: palette(grey, medium);
      font-weight: normal;
      line-height: 1em;
    }
  }
  &__key {
    display: block;
    margin-bottom: 0.5em;
  }
  &__value {
    display: block;
    margin-bottom: 0.5em;
  }
  &__buttons {
    display: block;
    text-align: right;
    margin-top: 2em;
    display: flex;
    .re-button {
      margin-right: 0.5em;
      margin-bottom: 0;
      display: inline-block;
      width: 100%;
      min-height: 38px;
      &:last-child() {
        margin-right: 0;
      }
    }
  }
}
</style>
