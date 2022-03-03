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
  <span class="span__text">
    <EntityHighlight
      v-if="token.entity"
      :class="['color_' + tag_color, { zindex3: showEntitiesSelector }]"
      :span="token"
      :dataset="dataset"
      @openTagSelector="openTagSelector"
      @removeEntity="removeEntity"
    /><span
      @mousedown="startSelection"
      @mouseup="endSelection"
      @mouseover="overSelection"
      v-else
      v-for="(t, i) in token.tokens"
      :key="i"
      v-html="
        `${$highlightSearch(dataset.query.text, t.text)}${
          token.hasSpaceAfter ? ' ' : ''
        }`
      "
    ></span
    ><lazy-entities-selector
      :dataset="dataset"
      :suggestedLabel="suggestedLabel"
      :token="token"
      :formattedEntities="formattedEntities"
      :showEntitiesSelector="showEntitiesSelector"
      v-if="showEntitiesSelector"
      @selectEntity="onSelectEntity"
      @changeEntityLabel="onChangeEntity"
      v-click-outside="onClickOutside"
    />
  </span>
</template>

<script>
import ClickOutside from "v-click-outside";

export default {
  directives: {
    clickOutside: ClickOutside.directive,
  },
  props: {
    record: {
      type: Object,
      required: true,
    },
    dataset: {
      type: Object,
      required: true,
    },
    suggestedLabel: {
      type: String,
    },
    token: {
      type: Object,
      required: true,
    },
    spanId: {
      type: Number,
      required: true,
    },
  },
  data: () => ({
    showEntitiesSelector: false,
  }),
  computed: {
    tag_color() {
      return this.dataset.entities.filter(
        (entity) => entity.text === this.token.entity.label
      )[0].colorId;
    },
    filteredEntities() {
      return this.dataset.entities
        .filter((entity) => entity.text)
        .sort((a, b) => a.text.localeCompare(b.text));
    },
    formattedEntities() {
      const characters = "1234567890".split("");
      return this.filteredEntities.map((ent, index) => ({
        ...ent,
        shortCut: characters[index],
      }));
    },
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
  },
  watch: {
    async showEntitiesSelector(n, o) {
      if (n !== o) {
        await this.dataset.viewSettings.disableShortCutPagination(n);
      }
    },
  },
  methods: {
    startSelection() {
      if (this.annotationEnabled) {
        this.$emit("endSelection", undefined);
        this.$emit("startSelection", this.spanId);
      }
    },
    overSelection() {
      if (this.annotationEnabled) {
        this.$emit("overSelection", this.spanId);
      }
    },
    endSelection() {
      if (this.annotationEnabled) {
        this.$emit("endSelection", this.spanId);
        if (this.formattedEntities.length == 1) {
          this.onSelectEntity(this.formattedEntities[0].text);
        } else {
          this.showEntitiesSelector = true;
        }
      }
    },
    openTagSelector() {
      if (this.token.origin !== "prediction") {
        this.showEntitiesSelector = !this.showEntitiesSelector;
        this.startSelection();
        this.endSelection();
      }
    },
    removeEntity() {
      this.$emit("removeEntity", this.token.entity);
      this.showEntitiesSelector = false;
    },
    onClickOutside() {
      this.showEntitiesSelector = false;
    },
    onSelectEntity(entityLabel) {
      this.$emit("selectEntity", entityLabel);
      this.showEntitiesSelector = false;
    },
    onChangeEntity(token, entityLabel) {
      this.$emit("changeEntityLabel", token, entityLabel);
      this.showEntitiesSelector = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.span {
  position: relative;
  display: inline;
  line-height: 18px;
  @include font-size(0);
  &__text {
    display: inline;
    position: relative;
    @include font-size(18px);
    margin: 0 -1.5px;
    padding: 0 1.5px;
  }
  &__whitespace {
    @include font-size(18px);
    cursor: default !important;
  }
}

// highlight word with overlay
.zindex3 {
  z-index: 3;
}
.selected {
  cursor: pointer;
  position: relative;
  background: palette(grey, smooth);
  .prediction ::v-deep .highlight__content {
    background: palette(grey, smooth);
  }
  .span__text {
    background: palette(grey, smooth);
  }
  .span__whitespace {
    background: palette(grey, smooth);
  }
}
.last-selected {
  .span__whitespace {
    background: none;
  }
}
.list__item--annotation-mode span span {
  cursor: text;
}
// ner colors

$colors: 50;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(($colors * $i) + ($hue * $i / $colors), 100%, 88%, 1);
  .color_#{$i - 1} {
    &.annotation ::v-deep .highlight__content {
      background: $rcolor;
    }
    &.prediction ::v-deep .highlight__content {
      padding-bottom: 3px;
      border-bottom: 5px solid $rcolor;
    }
    &.annotation ::v-deep .highlight__tooltip:after {
      border-color: $rcolor transparent transparent transparent;
    }
    &.prediction ::v-deep .highlight__tooltip:after {
      border-color: transparent transparent $rcolor transparent;
    }
    &.active,
    &.tag:hover {
      border: 2px solid darken($rcolor, 50%);
    }
  }
  .tag.color_#{$i - 1} span {
    background: $rcolor;
  }
  ::v-deep .entities__selector__option.color_#{$i - 1} {
    background: $rcolor;
    border: 2px solid $rcolor;
  }
  ::v-deep .entities__selector__option.color_#{$i - 1} {
    &:active,
    &.active,
    &:hover {
      border: 2px solid mix(black, $rcolor, 20%);
    }
  }
  .color_#{$i - 1} ::v-deep .highlight__tooltip {
    background: $rcolor;
  }
}
</style>
