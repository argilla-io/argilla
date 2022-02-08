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
        v-click-outside="onClickOutside"
        v-if="showEntitiesSelector"
        class="entities__selector"
      >
        <span v-show="!addnewSlotVisible">
          <ul class="entities__selector__options">
            <li
              class="entities__selector__option suggestion"
              :class="[
                `color_${suggestedEntity.colorId}`,
                activeEntity === -1 ? 'active' : null,
              ]"
              v-if="suggestedEntity"
              @click="selectEntity(suggestedEntity)"
            >
              <span>{{ suggestedEntity.text }}</span>
              <span class="entity__sort-code">[space]</span>
            </li>
            <li
              class="entities__selector__option suggestion"
              :class="[
                `color_${lastSelectedEntity.colorId}`,
                activeEntity === -1 ? 'active' : null,
              ]"
              v-else-if="lastSelectedEntity.text"
              @click="selectEntity(lastSelectedEntity)"
            >
              <span>{{ lastSelectedEntity.text }}</span>
              <span class="entity__sort-code">[space]</span>
            </li>
            <li
              v-for="(entity, index) in formattedEntities"
              tabindex="0"
              :focused="activeEntity === index"
              :key="index"
              class="entities__selector__option"
              :class="[
                `color_${entity.colorId}`,
                activeEntity === index ? 'active' : null,
              ]"
              @click="selectEntity(entity)"
            >
              <span>{{ entity.text }}</span>
              <span class="entity__sort-code"
                >[{{
                  activeEntity === index ? "enter" : entity.shortCut
                }}]</span
              >
            </li>
          </ul>
        </span>
      </div>
    </span>
    <span class="span__whitespace" v-html="whiteSpace"></span>
  </span>
</template>

<script>
import ClickOutside from "v-click-outside";
import "assets/icons/cross";
import { substring } from "stringz";
import { mapActions } from "vuex";

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
    suggestedLabel: {
      type: String,
    },
  },
  data: () => ({
    newSlot: "",
    showEntitiesSelector: false,
    addnewSlotVisible: false,
    controlPressed: false,
    controlKey: undefined,
    activeEntity: -1,
  }),
  computed: {
    span() {
      return this.spans[this.spanId];
    },
    lastSelectedEntity() {
      return this.dataset.lastSelectedEntity;
    },
    text() {
      return substring(
        this.record.text,
        this.spans[this.spanId].start,
        this.spans[this.spanId].end
      );
    },
    whiteSpace() {
      return substring(
        this.record.text,
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
    suggestedEntity() {
      return this.formattedEntities.find(
        (ent) => ent.text === this.suggestedLabel
      );
    },
  },
  mounted() {
    window.addEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  methods: {
    ...mapActions({
      updateLastSelectedEntity:
        "entities/token_classification/updateLastSelectedEntity",
    }),
    startSelection() {
      if (this.annotationEnabled) {
        this.$emit("endSelection", undefined);
        this.$emit("startSelection", this.spanId);
      }
    },
    endSelection() {
      if (this.annotationEnabled) {
        this.$emit("endSelection", this.spanId);
        if (this.formattedEntities.length == 1) {
          this.selectEntity(this.formattedEntities[0]);
        } else {
          this.showEntitiesSelector = true;
        }
      }
    },
    openTagSelector() {
      if (this.span.origin !== "prediction") {
        this.showEntitiesSelector = !this.showEntitiesSelector;
        this.startSelection();
        this.endSelection();
      }
    },
    removeEntity() {
      this.$emit("removeEntity", this.span.entity);
      this.showEntitiesSelector = false;
    },
    onClickOutside() {
      this.showEntitiesSelector = false;
    },
    async selectEntity(entityLabel) {
      await this.updateLastSelectedEntity({
        dataset: this.dataset,
        lastSelectedEntity: entityLabel,
      });
      this.span.entity
        ? this.$emit("changeEntityLabel", this.span.entity, entityLabel.text)
        : this.$emit("selectEntity", entityLabel.text);
      this.showEntitiesSelector = false;
      this.resetActiveEntity();
    },
    keyUp(event) {
      if (this.controlKey === event.key) {
        this.controlPressed = false;
      }
    },
    resetActiveEntity() {
      this.activeEntity = -1;
    },
    keyDown(event) {
      if (event.ctrlKey) {
        this.controlKey = event.key;
        this.controlPressed = true;
      }
      const cmd = String.fromCharCode(event.keyCode).toUpperCase();
      if (this.showEntitiesSelector && cmd) {
        const element = document.getElementsByClassName("active");
        event.preventDefault();
        // enter
        if (event.keyCode === 13) {
          if (this.activeEntity !== -1) {
            this.selectEntity(this.formattedEntities[this.activeEntity]);
          }
          //space
        } else if (event.keyCode === 32) {
          if (this.suggestedEntity) {
            this.selectEntity(this.suggestedEntity);
          } else if (this.lastSelectedEntity) {
            this.selectEntity(this.lastSelectedEntity);
          }
          //down
        } else if (
          event.keyCode === 40 &&
          this.activeEntity + 1 < this.formattedEntities.length
        ) {
          this.activeEntity++;
          if (element[0] && element[0].offsetTop >= 90) {
            element[0].parentNode.scrollTop = element[0].offsetTop - 2;
          }
          //up
        } else if (event.keyCode === 38 && this.activeEntity >= 0) {
          this.activeEntity--;
          if (element[0]) {
            element[0].parentNode.scrollTop =
              element[0].offsetTop - element[0].offsetHeight - 8;
          }
        } else {
          const entity = this.formattedEntities.find((t) => t.shortCut === cmd);
          if (entity) {
            this.selectEntity(entity);
          }
        }
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.entities {
  &__selector {
    position: absolute;
    left: -35%;
    top: 1em;
    min-width: 220px;
    z-index: 9;
    background: palette(grey, smooth);
    font-weight: 600;
    padding: 0.8em;
    border-radius: 1px;
    &__container {
      @include font-size(14px);
      line-height: 1em;
      display: inline-block;
      white-space: pre-line;
    }
    &__options {
      max-height: 142px;
      overflow-y: scroll;
      padding-left: 0;
      margin: 0;
      overscroll-behavior: contain;
      position: relative;
    }
    &__option {
      display: flex;
      transition: all 0.2s ease;
      padding: 0.5em;
      position: relative;
      cursor: pointer;
      margin-top: 2px;
      margin-bottom: 2px;
      &.suggestion {
        margin-bottom: 0.5em;
      }
      span {
        cursor: pointer !important;
      }
    }
  }
}
.span {
  position: relative;
  display: inline;
  line-height: 18px;
  @include font-size(0);
  &::selection {
    background: none !important;
  }
  &__text {
    display: inline;
    position: relative;
    @include font-size(18px);
  }
  &__whitespace {
    @include font-size(18px);
    &::selection {
      background: none !important;
    }
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
  span::selection {
    background: none !important;
  }
  ::v-deep .highlight-text {
    &::selection {
      background: none !important;
    }
  }
}
.last-selected {
  .span__whitespace {
    background: none;
  }
}
.span span {
  display: inline;
  &::selection {
    background: palette(grey, smooth);
  }
  ::v-deep .highlight-text {
    &::selection {
      background: palette(grey, smooth);
    }
  }
}
.list__item--annotation-mode span span {
  cursor: text;
}
.entity {
  &.non-selectable,
  &.non-selectable--show-sort-code {
    cursor: default;
    pointer-events: none;
  }
  &__sort-code {
    margin-left: auto;
    margin-right: 0;
    .non-selectable & {
      display: none;
    }
  }
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
  .entities__selector__option.color_#{$i - 1} {
    background: $rcolor;
    border: 2px solid $rcolor;
  }
  .entities__selector__option.color_#{$i - 1} {
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
