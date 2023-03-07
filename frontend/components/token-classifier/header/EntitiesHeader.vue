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
  <div class="container">
    <div class="entities__wrapper">
      <div v-if="visibleEntities.length" class="entities__container">
        <entity-label
          v-for="(entity, index) in visibleEntities"
          :label="entity.text"
          :shortcut="entity.shortcut"
          :key="index"
          :color="`color_${entity.colorId % $entitiesMaxColors}`"
        />
        <base-button
          v-if="isCollapsable"
          class="entities__container__button secondary text"
          @click="toggleEntitiesNumber"
          >{{ buttonText }}</base-button
        >
      </div>
    </div>
  </div>
</template>

<script>
const MAX_ENTITIES_SHOWN = 10;

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    showExpandedList: false,
    maxEntitiesNumber: MAX_ENTITIES_SHOWN,
  }),
  computed: {
    visibleEntities() {
      const characters = "1234567890".split("");
      let entities = [...this.dataset.entities]
        .sort((a, b) => a.text.localeCompare(b.text))
        .map((ent, index) => ({
          shortcut: characters[index],
          ...ent,
        }));

      return this.showExpandedList ? entities : this.showMaxEntities(entities);
    },
    entitiesNumber() {
      return this.dataset.entities?.length || null;
    },
    isCollapsable() {
      return this.entitiesNumber > this.maxEntitiesNumber;
    },
    buttonText() {
      return this.showExpandedList
        ? `Show less`
        : `+ ${this.entitiesNumber - this.maxEntitiesNumber}`;
    },
  },
  methods: {
    toggleEntitiesNumber() {
      this.showExpandedList = !this.showExpandedList;
    },
    showMaxEntities(entities) {
      return entities.slice(0, this.maxEntitiesNumber);
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
  margin-left: 0;
  @extend %collapsable-if-metrics !optional;
}
.entities {
  &__wrapper {
    position: relative;
  }
  &__container {
    margin-bottom: $base-space;
    border-radius: $border-radius-m;
    max-height: 189px;
    overflow: auto;
    @extend %hide-scrollbar;
    .--annotation & {
      margin-bottom: $base-space * 2;
    }
    &__button {
      display: inline-block;
    }
  }
}
.entity-label {
  margin: 4px;
}
</style>
