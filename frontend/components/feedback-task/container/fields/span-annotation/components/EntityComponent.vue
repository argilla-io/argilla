<template>
  <span class="span-entity__wrapper">
    <template v-if="allowOverlapping">
      <span
        v-for="(line, index) in lines"
        :key="index"
        class="span-entity__line"
        :style="{
          width: line.width,
          left: line.left,
          top: line.top,
        }"
      ></span>
    </template>
    <div
      class="span-entity__container"
      :style="{
        left: `${entityPosition.left}px`,
        top: `${entityPosition.top}px`,
      }"
      ref="spanEntityRef"
      id="spanEntity"
    >
      <div
        v-on="!singleOption ? { click: toggleDropdown } : {}"
        @mouseenter="hoverSpan(true)"
        @mouseleave="hoverSpan(false)"
        :class="[
          !singleOption ? 'span-entity--clickable' : 'span-entity',
          allowOverlapping ? 'span-entity--overlapping' : null,
        ]"
        v-if="!visibleDropdown"
      >
        <BaseButton
          class="span-entity__close-button"
          @click="removeSelectedOption"
        >
          <svgicon
            class="span-entity__close-button__icon"
            name="close"
            width="10"
            height="10"
        /></BaseButton>
        <span class="span-entity__text" v-text="selectedOption.text" />
        <svgicon
          v-if="!!suggestion"
          class="span-entity__suggestion"
          name="suggestion"
          width="8"
          height="8"
        />
        <span
          v-if="suggestionScore"
          class="span-entity__score"
          v-text="suggestionScore"
        />
      </div>
      <EntityComponentDropdown
        v-else
        :style="{
          left: `${spanEntityPosition.left}px`,
          top: `${spanEntityPosition.top}px`,
        }"
        :selectedOption="selectedOption"
        :options="options"
        @on-replace-option="selectOption"
        @on-remove-option="removeSelectedOption"
        v-click-outside="hideDropdown"
      />
    </div>
  </span>
</template>

<script>
import "assets/icons/close";
import "assets/icons/suggestion";

export default {
  name: "EntityComponent",
  props: {
    entity: {
      type: Object,
      required: true,
    },
    spanQuestion: {
      type: Object,
    },
    suggestion: {
      type: Object,
    },
    entityPosition: {
      type: Object,
      required: true,
    },
    lineHeight: {
      type: Number,
    },
  },
  data() {
    return {
      visibleDropdown: false,
      spanEntityPosition: {
        left: "0px",
        top: "0px",
      },
    };
  },
  computed: {
    selectedOption() {
      return this.options.find((e) => e.id === this.entity.id);
    },
    options() {
      return this.spanQuestion.answer.options;
    },
    singleOption() {
      return this.options.length === 1;
    },
    suggestionScore() {
      return this.suggestion?.score?.toFixed(1);
    },
    entityColor() {
      return this.entity.color;
    },
    allowOverlapping() {
      // return this.spanQuestion.settings.allow_overlapping;
      return true;
    },
    lines() {
      const lines = [];
      const { width, top, topEnd, left, right } = this.entityPosition;
      const space = topEnd - top;
      const linesCount = this.getNumberOfLines(space);
      if (linesCount === 1) {
        return [
          {
            width: `${width}px`,
            left: `${left}px`,
            top: `${top}px`,
          },
        ];
      }

      const firstLine = 0;
      const lastLine = linesCount - 1;

      for (let i = 0; i < linesCount; i++) {
        lines.push({
          width:
            i === firstLine
              ? `${width - left}px`
              : i === lastLine
              ? `${right}px`
              : `${width}px`,
          left: i === 0 ? `${left}px` : 0,
          top: `${top + i * this.lineHeight}px`,
        });
      }

      return lines;
    },
  },
  methods: {
    getNumberOfLines(space) {
      return Math.floor(space / this.lineHeight + 1) || 1;
    },
    selectOption(option) {
      this.$emit("on-replace-option", option);
      this.hideDropdown();
    },
    removeSelectedOption() {
      this.$emit("on-remove-option");
      this.hideDropdown();
    },
    hoverSpan(isHovered) {
      if (this.allowOverlapping) {
        this.$emit("on-hover-span", isHovered);
      }
    },
    toggleDropdown() {
      this.visibleDropdown = !this.visibleDropdown;
      this.getPosition();
    },
    hideDropdown() {
      this.visibleDropdown = false;
    },
    getPosition() {
      const position = this.$refs.spanEntityRef.getBoundingClientRect();
      this.spanEntityPosition.left = position.left;
      this.spanEntityPosition.top =
        position.top + this.$refs.spanEntityRef.scrollTop;
    },
    getScrollParent(element) {
      if (!element) return;

      let parent = element.parentElement;
      while (parent) {
        const { overflow } = window.getComputedStyle(parent);
        if (overflow.split(" ").every((o) => o === "auto" || o === "scroll")) {
          return parent;
        }

        parent = parent.parentElement;
      }

      return document.documentElement;
    },
  },
  mounted() {
    this.scroll = this.getScrollParent(document.getElementById("spanEntity"));

    if (this.scroll) {
      this.scroll.addEventListener("scroll", this.getPosition);
    }
  },
  beforeDestroy() {
    if (this.scroll) {
      this.scroll.removeEventListener("scroll", this.getPosition);
    }
  },
};
</script>

<style lang="scss" scoped>
@import url("https://fonts.googleapis.com/css2?family=Roboto+Condensed&display=swap");
.span-entity {
  $this: &;
  display: flex;
  gap: 2px;
  align-items: center;
  flex-shrink: 0;
  min-width: 10px;
  max-width: v-bind("entityPosition.width");
  margin-top: -1px;
  padding-right: 3px;
  text-transform: uppercase;
  font-family: "Roboto Condensed", sans-serif;
  user-select: none;
  transform-origin: left top;
  transition: scale 0.2s;
  &:before {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 0;
    z-index: -1;
    transition: width 0.2s ease;
  }
  &__wrapper {
    position: static;
  }
  &__container {
    position: absolute;
    display: flex;
    margin-top: 20px;
    line-height: 1.2;
    @include font-size(11px);
  }
  &__score {
    display: none;
    margin-left: 2px;
  }
  &__text {
    gap: 4px;
    @include truncate(auto);
  }
  &__line {
    position: absolute;
    height: 2px;
    background: v-bind(entityColor);
    margin-top: 20px;
  }
  &:hover {
    position: relative;
    z-index: 1;
    transition: scale 0.2s;
    max-width: none;
    scale: 1.1;
    #{$this}__close-button {
      display: inline-flex;
    }
    #{$this}__score {
      display: inline-flex;
    }
    &:before {
      background: v-bind("selectedOption.color");
      width: 100%;
      transition: width 0.2s ease;
    }
  }
  &__close-button {
    display: none;
    height: 100%;
    padding: 0 1px;
    margin-right: calc($base-space / 2);
    flex-shrink: 0;
    border-radius: 0;
    background: $black-54;
    &:hover {
      background: $black-87;
    }
    &__icon {
      min-width: 10px;
      color: palette(white);
    }
  }
  &--clickable {
    cursor: pointer;
    @extend .span-entity;
  }
  &--overlapping {
    @extend .span-entity;
    background: v-bind(entityColor);
    margin-top: 0;
  }
}
</style>
