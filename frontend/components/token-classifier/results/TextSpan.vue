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
  <span class="span">
    <EntityHighlight
      v-if="span.entity"
      :text="text"
      :class="['color_' + tag_color, { zindex3: showEntitiesSelector }]"
      :span="span"
      :dataset="dataset"
      @openTagSelector="openTagSelector"
      @removeEntity="removeEntity"
    />
    <span
      v-else
      class="span__text"
      @mousedown="startSelection"
      @mouseup="endSelection"
      v-html="$highlightSearch(dataset.query.text, text)"
    /><span class="entities__selector__container">
      <div
        v-if="showEntitiesSelector"
        v-click-outside="onClickOutside"
        class="entities__selector"
      >
        <span v-show="!addnewSlotVisible">
          <input
            v-model="searchEntity"
            class="entities__selector__search"
            type="text"
            placeholder="Select entity..."
            @focus="isFocused = true"
          />
          <ul class="entities__selector__options">
            <li
              v-for="(entity, index) in formattedEntities"
              :key="index"
              class="entities__selector__option"
              :class="`color_${entity.colorId}`"
              @click="selectEntity(entity.text)"
            >
              <span v-if="controlPressed" class="entity__sort-code"
                >[{{ entity.shortCut }}]</span
              >
              <span>{{ entity.text }}</span>
              <svgicon
                v-if="span.entity && entity.text === span.entity.label"
                color="#bababa"
                name="check"
              />
            </li>
          </ul>
        </span>
      </div>
      <div v-if="showEntitiesSelector" class="overlay" />
    </span>
    <span class="span__whitespace" v-html="whiteSpace"></span>
  </span>
</template>

<script>
import ClickOutside from "v-click-outside";
import "assets/icons/check";
import "assets/icons/cross";

export default {
  directives: {
    clickOutside: ClickOutside.directive,
  },
  props: {
    record: {
      type: Object,
      required: true,
    },
    spanId: {
      type: Number,
      required: true,
    },
    spans: {
      type: Array,
      required: true,
    },
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    searchEntity: "",
    newSlot: "",
    showEntitiesSelector: false,
    addnewSlotVisible: false,
    isFocused: false,
    controlPressed: false,
    controlKey: undefined,
  }),
  computed: {
    span() {
      return this.spans[this.spanId];
    },
    text() {
      return this.record.raw_text.slice(
        this.spans[this.spanId].start,
        this.spans[this.spanId].end
      );
    },
    whiteSpace() {
      return this.record.raw_text.slice(
        this.spans[this.spanId].end,
        this.spans[this.spanId + 1] ? this.spans[this.spanId + 1].start : ""
      );
    },
    tag_color() {
      return this.dataset.entities.filter(
        (entity) => entity.text === this.span.entity.label
      )[0].colorId;
    },
    filteredEntities() {
      return this.dataset.entities
        .filter((entity) =>
          entity.text.toLowerCase().includes(this.searchEntity.toLowerCase())
        )
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
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
  created() {
    window.addEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  methods: {
    startSelection() {
      if (this.annotationEnabled) {
        this.$emit("startSelection", this.spanId);
      }
    },
    endSelection() {
      if (this.annotationEnabled) {
        this.$emit("endSelection", this.spanId);
        this.showEntitiesSelector = true;
        // TODO (@leireaguirrework) : What's the purpose of this block?
        if (this.activeTag) {
          this.selectEntity(this.activeTag);
          // remove selection highlight after apply tag
          const selectionHighlight = window.getSelection();
          selectionHighlight.removeAllRanges();
        }
      }
    },
    openTagSelector() {
      this.showEntitiesSelector = !this.showEntitiesSelector;
      this.startSelection();
      this.endSelection();
    },
    removeEntity() {
      this.$emit("removeEntity", this.span.entity);
      this.showEntitiesSelector = false;
    },
    onClickOutside() {
      this.showEntitiesSelector = false;
      this.searchEntity = "";
      this.$emit("reset");
    },
    selectEntity(entityLabel) {
      this.span.entity
        ? this.$emit("changeEntityLabel", this.span.entity, entityLabel)
        : this.$emit("selectEntity", entityLabel);
      this.showEntitiesSelector = false;
      this.searchEntity = "";
    },
    keyUp(event) {
      if (this.controlKey === event.key) {
        this.controlPressed = false;
      }
    },
    keyDown(event) {
      if (event.ctrlKey) {
        this.controlKey = event.key;
        this.controlPressed = true;
      }
      const cmd = String.fromCharCode(event.keyCode).toUpperCase();
      if (this.controlPressed && this.showEntitiesSelector && cmd) {
        const entity = this.formattedEntities.find((t) => t.shortCut === cmd);
        if (entity) {
          this.selectEntity(entity.text);
        }
      }
    },
  },
};
</script>
<style lang="scss">
.highlight-text {
  display: inline-block;
  background: #ffbf00 !important;
  line-height: 16px;
}
</style>
<style lang="scss" scoped>
.entities {
  &__selector {
    position: absolute;
    left: -35%;
    top: 2em;
    min-width: 160px;
    z-index: 9;
    background: white;
    border: 1px solid $primary-color;
    font-weight: 500;
    &__container {
      @include font-size(14px);
      line-height: 1em;
      display: inline-block;
      white-space: pre-line;
    }
    &__search {
      width: 100%;
      padding: 0.5em;
      border: 0;
      outline: none;
      background: $lighter-color;
      border-bottom: 1px solid $line-light-color;
    }
    &__options {
      max-height: 146px;
      overflow-y: scroll;
      padding-left: 0;
    }
    &__option {
      display: flex;
      transition: all 0.2s ease;
      padding: 5px;
      padding-right: 2em;
      position: relative;
      cursor: pointer;
      span {
        padding: 3px;
      }
      .svg-icon {
        position: absolute;
        right: 0.5em;
        top: 1em;
        margin: auto 0 auto auto;
        @include font-size(12px);
      }
    }
  }
}
.span {
  position: relative;
  display: inline;
  line-height: 1em;
  @include font-size(0);
  &__text {
    @include font-size(16px);
    display: inline;
    position: relative;
  }
  &__whitespace {
    @include font-size(16px);
  }
}

.overlay {
  background: white;
  opacity: 0.5;
  height: 100vh;
  position: fixed;
  width: 100vw;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
}

// highlight word with overlay
.zindex3 {
  z-index: 3;
}
.selected {
  // border: 1px dashed $tertiary-color;
  .span__text {
    line-height: 1.5em;
    background: $tertiary-lighten-color;
  }
}
.span span {
  &::selection {
    background: $tertiary-lighten-color;
  }
}
.entity {
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
    ::v-deep span {
      background: $rcolor;
    }
    &.active,
    &.tag:hover {
      border: 2px solid darken($rcolor, 50%);
    }
  }
  .tag.color_#{$i - 1} span {
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
