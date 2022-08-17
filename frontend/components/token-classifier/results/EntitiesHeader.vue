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
        <span
          v-for="(entity, index) in visibleEntities"
          :key="index"
          class="entity"
          :class="[
            `color_${entity.colorId % $entitiesMaxColors}`,
            activeEntity === entity.text ? 'active' : '',
          ]"
        >
          {{ entity.text }}
          <span v-if="entity.shortcut" class="shortcut"
            >[{{ entity.shortcut }}]</span
          >
        </span>
        <base-button
          v-if="!showEntitySelector && dataset.entities.length > entitiesNumber"
          class="entities__container__button primary clear small"
          @click="toggleEntitiesNumber"
          >{{ `+ ${dataset.entities.length - entitiesNumber}` }}</base-button
        >
      </div>
      <base-button
        v-if="showEntitySelector && dataset.entities.length > entitiesNumber"
        class="entities__container__button primary clear small fixed"
        @click="toggleEntitiesNumber"
        >{{ "Show less" }}</base-button
      >
    </div>
  </div>
</template>

<script>
import "assets/icons/check";
import "assets/icons/close";
const MAX_ENTITIES_SHOWN = 10;

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    activeEntity: undefined,
    showEntitySelector: false,
    entitiesNumber: MAX_ENTITIES_SHOWN,
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

      return this.showEntitySelector
        ? entities
        : entities.slice(0, this.entitiesNumber);
    },
  },
  methods: {
    toggleEntitiesNumber() {
      this.showEntitySelector = !this.showEntitySelector;
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
    padding: 0.4em 0.5em;
    margin-bottom: $base-space * 2;
    background: palette(white);
    border-radius: $border-radius-m;
    box-shadow: $shadow-300;
    min-height: 48px;
    max-height: 189px;
    overflow: auto;
    @extend %hide-scrollbar;
    &__button {
      margin-top: -1px;
      margin-left: 0.3em;
      display: inline-block;
      &.fixed {
        position: absolute;
        right: $base-space;
        bottom: $base-space;
        background: rgba(255, 255, 255, 80%);
      }
    }
  }
}
.entity {
  padding: 0.3em;
  margin: 4px;
  position: relative;
  display: inline-flex;
  align-items: center;
  max-height: 28px;
  border: 2px solid transparent;
  transition: all 0.2s ease-in-out;
  font-weight: 600;
  .shortcut {
    @include font-size(14px);
    font-weight: lighter;
    margin-left: $base-space * 2;
  }
}
// ner colors

$colors: 50;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(($colors * $i) + calc($hue * $i / $colors), 100%, 88%, 1);
  .color_#{$i - 1} {
    background: $rcolor;
  }
  .entity.color_#{$i - 1} span {
    background: $rcolor;
  }
  .entities__selector__option.color_#{$i - 1} span {
    background: $rcolor;
  }
  .color_#{$i - 1} :deep(.highlight__tooltip) {
    background: $rcolor;
  }
  .color_#{$i - 1} :deep(.highlight__tooltip:after) {
    border-color: $rcolor transparent transparent transparent;
  }
}
</style>
