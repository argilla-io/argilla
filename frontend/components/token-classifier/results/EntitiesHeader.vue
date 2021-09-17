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
  <div
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
        `color_${entity.colorId}`,
        activeEntity === entity.text ? 'active' : '',
        annotationEnabled ? 'non-selectable--show-sort-code' : 'non-selectable',
      ]"
      @click="onActiveEntity(entity)"
    >
      {{ entity.text }}
    </span>
    <ReButton
      v-if="dataset.entities.length > entitiesNumber"
      class="entities__container__button"
      @click="toggleEntitiesNumber"
      >{{ showEntitySelector ? "Show less" : "Show all" }}</ReButton
    >
  </div>
</template>

<script>
import "assets/icons/check";
import "assets/icons/cross";
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
      let entities = [...this.dataset.entities]
        .sort((a, b) => a.text.localeCompare(b.text))
        .map((ent) => ({
          ...ent,
        }));

      return this.showEntitySelector
        ? entities
        : entities.slice(0, this.entitiesNumber);
    },
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
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
.entities {
  &__container {
    margin-bottom: 1em;
    padding: 0 4em;
    width: calc(100% - 120px);
    @include media(">desktopLarge") {
      width: calc(100% - 360px);
    }
    &__button {
      margin-top: 0.3em;
      margin-left: 0.3em;
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
  margin: 1em 1em 0 0;
  position: relative;
  display: inline-block;
  cursor: pointer;
  max-height: 28px;
  border: 2px solid transparent;
  transition: all 0.2s ease-in-out;
  // &:not(.active):hover {
  //   filter: brightness(90%);
  // }
  &.non-selectable,
  &.non-selectable--show-sort-code {
    cursor: default;
    pointer-events: none;
  }
  &__sort-code {
    @include font-size(12px);
    color: $font-medium-color;
    font-weight: lighter;
    margin-left: 0.5em;
    .non-selectable & {
      display: none;
    }
  }
}
// ner colors

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
  .entities__selector__option.color_#{$i - 1} {
    background: white;
    &:hover {
      background: hsla(($colors * $i) + ($hue * $i / $colors), 100%, 97%, 1);
    }
    &:active {
      background: hsla(($colors * $i) + ($hue * $i / $colors), 100%, 94%, 1);
    }
  }
  .color_#{$i - 1} ::v-deep .highlight__tooltip {
    background: $rcolor;
  }
  .color_#{$i - 1} ::v-deep .highlight__tooltip:after {
    border-color: $rcolor transparent transparent transparent;
  }
}
</style>
