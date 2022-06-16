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
      <div
        v-if="visibleEntities.length"
        :class="[
          'entities__container',
          activeEntity ? 'entities__container--multiple' : '',
        ]"
      >
        <span
          v-for="(entity, index) in visibleEntities"
          :key="index"
          class="entity"
          :class="[
            `color_${entity.colorId % $entitiesMaxColors}`,
            activeEntity === entity.text ? 'active' : '',
            annotationEnabled
              ? 'non-selectable--show-sort-code'
              : 'non-selectable',
          ]"
          @click="onActiveEntity(entity)"
        >
          {{ entity.text }}
          <span v-if="entity.shortcut" class="shortcut"
            >[{{ entity.shortcut }}]</span
          >
        </span>
        <ReButton
          v-if="!showEntitySelector && dataset.entities.length > entitiesNumber"
          class="entities__container__button"
          @click="toggleEntitiesNumber"
          >{{ `+ ${dataset.entities.length - entitiesNumber}` }}</ReButton
        >
      </div>
      <ReButton
        v-if="showEntitySelector && dataset.entities.length > entitiesNumber"
        class="entities__container__button fixed"
        @click="toggleEntitiesNumber"
        >{{ "Show less" }}</ReButton
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
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
  },
  methods: {
    toggleEntitiesNumber() {
      this.showEntitySelector = !this.showEntitySelector;
    },
    onActiveEntity(entity) {
      if (this.annotationEnabled) {
        if (this.activeEntity === entity.text) {
          this.activeEntity = undefined;
        } else {
          this.activeEntity = entity.text;
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  @extend %container;
  padding-top: 0;
  padding-bottom: 0.7em;
  margin-left: 0;
  @extend %collapsable-if-metrics !optional;
}
.entities {
  &__wrapper {
    position: relative;
  }
  &__container {
    padding: 0.4em 0.5em;
    background: palette(white);
    border-radius: $border-radius;
    box-shadow: 0 1px 2px 0 rgba(185, 185, 185, 0.5);
    min-height: 48px;
    max-height: 189px;
    overflow: auto;
    @extend %hide-scrollbar;
    &__button {
      margin-top: 0.3em;
      margin-left: 0.3em;
      padding: 0.5em;
      transition: background 0.2s ease-in-out;
      padding: 5px;
      border-radius: $border-radius;
      border: 0;
      background: none;
      cursor: pointer;
      &:hover {
        background: $bg !important;
        transition: background 0.2s ease-in-out;
      }
      &.fixed {
        position: absolute;
        right: 8px;
        bottom: 8px;
        background: rgba(255, 255, 255, 80%);
      }
    }
    &--multiple {
      .entity:not(.active) {
        // opacity: 0.7;
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
  cursor: pointer;
  max-height: 28px;
  border: 2px solid transparent;
  transition: all 0.2s ease-in-out;
  font-weight: 600;
  // &:not(.active):hover {
  //   filter: brightness(90%);
  // }
  &.non-selectable,
  &.non-selectable--show-sort-code {
    cursor: default;
    pointer-events: none;
  }
  .shortcut {
    @include font-size(14px);
    font-weight: lighter;
    margin-left: 1em;
    .non-selectable & {
      display: none;
    }
  }
}
// ner colors

$colors: 50;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(($colors * $i) + calc($hue * $i / $colors), 100%, 88%, 1);
  .color_#{$i - 1} {
    background: $rcolor;
    &.active,
    &.entity:hover {
      border: 2px solid darken($rcolor, 50%);
    }
  }
  .entity.color_#{$i - 1} span {
    background: $rcolor;
  }
  .entities__selector__option.color_#{$i - 1} span {
    background: $rcolor;
  }
  .color_#{$i - 1} ::v-deep .highlight__tooltip {
    background: $rcolor;
  }
  .color_#{$i - 1} ::v-deep .highlight__tooltip:after {
    border-color: $rcolor transparent transparent transparent;
  }
}
</style>
