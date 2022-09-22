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
  <div>
    <p class="metrics__title">Stats</p>
    <stats-selector
      :selected-option="selectedOption"
      :options="options"
      @selectOption="onSelectOption"
    />
    <div v-if="selectedOption.id === 'mentions'">
      <div class="sidebar__tabs">
        <a
          href="#"
          :class="activeTab === 'predicted_mentions' ? 'active' : ''"
          @click.prevent="filteredMentionsBy('predicted_mentions')"
          >Predicted as</a
        >
        <a
          href="#"
          :class="activeTab === 'mentions' ? 'active' : ''"
          @click.prevent="filteredMentionsBy('mentions')"
          >Annotated as</a
        >
      </div>
      <div class="scroll">
        <div v-if="!existMentions">
          <span class="sidebar__tabs__empty"
            >There are no
            {{ activeTab === "mentions" ? "annotations" : "predictions" }}</span
          >
        </div>
        <div
          v-for="(prop, key) in filteredMentions"
          v-else
          :key="key"
          :class="expandedMentionsGroup === key ? 'expanded' : ''"
        >
          <entity-label
            :is-prediction="activeTab === 'predicted_mentions'"
            :label="key"
            :color="`color_${
              entities.filter((e) => e.text === key)[0].colorId %
              $entitiesMaxColors
            }`"
          />
          <sidebar-collapsable-mentions
            :limit="
              expandedMentionsGroup && expandedMentionsGroup !== key
                ? 0
                : currentMentionsLength
            "
            :entities="entities"
            :k="key"
            :object="filteredMentions"
            @limit="onShowMore(key)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    limit: 3,
    currentMentionsLength: 3,
    visible: false,
    activeTab: "predicted_mentions",
    filteredMentions: [],
    expandedMentionsGroup: undefined,
    selectedOption: {
      id: "mentions",
      name: "Mentions",
    },
  }),
  computed: {
    options() {
      let options = [];
      options.push({
        id: "mentions",
        name: "Mentions",
      });
      return options;
    },
    existMentions() {
      return Object.keys(this.filteredMentions).length;
    },
    entities() {
      return this.dataset.entities;
    },
    query() {
      return this.dataset.query;
    },
  },
  watch: {
    query() {
      this.filteredMentions = this.dataset.results.aggregations[this.activeTab];
    },
  },
  mounted() {
    this.filteredMentions = this.dataset.results.aggregations[this.activeTab];
  },
  methods: {
    filteredMentionsBy(type) {
      this.activeTab = type;
      this.filteredMentions = this.dataset.results.aggregations[type];
      this.expandedMentionsGroup = undefined;
      this.currentMentionsLength = this.limit;
    },
    onSelectOption(opt) {
      this.selectedOption = opt;
    },
    onShowMore(k) {
      const itemsLenght = Object.keys(this.filteredMentions[k]).length;
      this.currentMentionsLength === this.limit
        ? (this.currentMentionsLength = itemsLenght)
        : (this.currentMentionsLength = this.limit);
      this.currentMentionsLength === itemsLenght
        ? (this.expandedMentionsGroup = k)
        : (this.expandedMentionsGroup = undefined);
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  &__tabs {
    display: flex;
    padding-bottom: 1em;
    &__empty {
      margin-top: 2em;
      display: inline-block;
    }
    a {
      font-family: $sff;
      width: 100%;
      border-radius: $border-radius;
      text-align: center;
      color: $font-secondary-medium;
      text-decoration: none;
      margin: 0 5px;
      outline: none;
      @include font-size(13px);
      padding: 0.5em;
      &.active {
        color: $primary-color;
        background: palette(grey, 600);
      }
      &:hover {
        background: palette(grey, 600);
      }
    }
  }
  .scroll {
    max-height: calc(100vh - 250px);
    padding-right: 1em;
    margin-right: -1em;
    overflow: auto;
    @extend %hide-scrollbar;
  }
}
</style>
