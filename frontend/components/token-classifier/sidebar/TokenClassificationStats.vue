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
    <p class="sidebar__title">Stats</p>
    <StatsSelector
      :selected-option="selectedOption"
      :options="options"
      @selectOption="onSelectOption"
    />
    <StatsErrorDistribution
      v-if="selectedOption.id === 'error'"
      :dataset="dataset"
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
          <span
            :class="[
              `color_${entities.filter((e) => e.text === key)[0].colorId}`,
              'entity',
            ]"
            >{{ key }}</span
          >
          <SidebarCollapsableMentions
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
    activeTab: "mentions",
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
      if (Object.values(this.dataset.results.aggregations.predicted).length) {
        options.push({
          id: "error",
          name: "Error Distribution",
        });
      }
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
    }
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
  &__title {
    color: $font-secondary-dark;
    margin-top: 0.5em;
    @include font-size(20px);
  }
}
.sidebar {
  &__tabs {
    display: flex;
    padding-bottom: 1em;
    &__empty {
      margin-top: 2em;
      display: inline-block;
    }
    a {
      width: 100%;
      border: 1px solid palette(grey, smooth);
      border-radius: 2px;
      text-align: center;
      color: $font-secondary;
      text-decoration: none;
      margin: 0 5px;
      outline: none;
      @include font-size(13px);
      padding: 0.3em;
      &.active {
        background: palette(grey, light);
      }
    }
  }
  p {
    display: flex;
    align-items: flex-end;
    font-size: 18px;
    font-size: 1.125rem;
    margin-top: 0;
    margin-bottom: 2em;
    font-weight: 600;
    svg {
      margin-right: 0.5em;
    }
  }
  .entity {
    margin-top: 1em;
    margin-bottom: 0.5em;
    padding: 0.5em;
    display: inline-flex;
  }
  .scroll {
    max-height: calc(100vh - 430px);
    padding-right: 1em;
    margin-right: -1em;
    overflow: auto;
  }
}
$colors: 50;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(
    ($colors * $i) + ($hue * $i / $colors),
    100% - $i / 2,
    82% - ($colors % $i),
    1
  );
  .color_#{$i - 1} {
    background: $rcolor;
  }
}
</style>
