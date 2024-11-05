<template>
  <span class="span-entity__wrapper" role="mark">
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
      :style="entityRelativePosition"
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
          @click.stop="removeSelectedSpan(span)"
        >
          <svgicon name="close" width="10" height="10" color="#fff"
        /></BaseButton>
        <span class="span-entity__text"
          ><span v-text="selectedOption.text"
        /></span>
        <svgicon
          v-if="!!suggestion"
          :class="
            suggestedScore
              ? 'span-entity__suggestion--score'
              : 'span-entity__suggestion'
          "
          name="suggestion"
          width="8"
          height="8"
        />
        <span
          v-if="suggestedScore"
          class="span-entity__score"
          v-text="suggestedScore"
        />
      </div>
      <template v-else>
        <EntityDropdownOverlapping
          v-if="allowOverlapping"
          :style="overlappingDropdownPosition"
          :selectedOption="selectedOption"
          :options="options"
          :spanInRange="spanInRange"
          @on-add-span-base-on="addSpanBaseOn"
          @on-remove-span="removeSelectedSpan"
          v-click-outside="hideDropdown"
        />
        <EntityDropdown
          v-else
          :style="entityFixedPosition"
          :selectedOption="selectedOption"
          :options="options"
          @on-replace-entity="selectEntity"
          v-click-outside="hideDropdown"
        />
      </template>
    </div>
  </span>
</template>

<script>
import "assets/icons/close";
import "assets/icons/suggestion";

export default {
  name: "EntityComponent",
  props: {
    span: {
      type: Object,
      required: true,
    },
    entity: {
      type: Object,
      required: true,
    },
    spanQuestion: {
      type: Object,
      required: true,
    },
    suggestion: {
      type: Object,
    },
    entityPosition: {
      type: Object,
      required: true,
    },
    spanInRange: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      visibleDropdown: false,
      spanEntityPosition: {
        left: 0,
        top: 0,
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
    suggestedScore() {
      return this.suggestion?.value.score?.fixed;
    },
    entityColor() {
      return this.entity.color;
    },
    allowOverlapping() {
      return this.spanQuestion.settings.allow_overlapping;
    },
    lines() {
      const lines = [];
      const { width, top, topEnd, left, right } = this.entityPosition;
      const space = topEnd - top;
      const linesCount = space > 0 ? this.getNumberOfLines(space) : 0;

      for (let i = 0; i <= linesCount; i++) {
        lines.push({
          width: linesCount
            ? i === 0
              ? `${width - left}px`
              : i === linesCount
              ? `${right}px`
              : `${width}px`
            : `${width}px`,
          left: i === 0 ? `${left}px` : 0,
          top: `${top + i * this.entityPosition.lineHeight}px`,
        });
      }

      return lines;
    },
    entityWidth() {
      return `${this.entityPosition.width}px`;
    },
    entityRelativePosition() {
      return {
        left: `${this.entityPosition.left}px`,
        top: `${this.entityPosition.top}px`,
      };
    },
    entityFixedPosition() {
      return {
        left: `${this.spanEntityPosition.left}px`,
        top: `${this.spanEntityPosition.top}px`,
      };
    },
    getLevelInEntitiesInRange() {
      return this.spanInRange.findIndex(
        ({ entity }) => entity.id === this.entity.id
      );
    },
    overlappingDropdownPosition() {
      return {
        left: `${this.spanEntityPosition.left}px`,
        top: `${
          this.spanEntityPosition.top -
          this.getLevelInEntitiesInRange * this.entityPosition.baseEntityGap
        }px`,
      };
    },
  },
  methods: {
    getNumberOfLines(space) {
      return Math.floor(space / this.entityPosition.lineHeight + 1);
    },
    addSpanBaseOn(span, entity) {
      this.$emit("on-add-span-base-on", span, entity);
      this.hideDropdown();
    },
    selectEntity(entity) {
      this.$emit("on-replace-entity", entity);
      this.hideDropdown();
    },
    removeSelectedSpan(span) {
      this.$emit("on-remove-span", span);
      this.hideDropdown();
    },
    hoverSpan(isHovered) {
      this.getPosition();
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
        const { "overflow-y": overflowY } = window.getComputedStyle(parent);
        if (overflowY.split(" ").every((o) => o === "auto" || o === "scroll")) {
          return parent;
        }

        parent = parent.parentElement;
      }

      return document.documentElement;
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.scroll = this.getScrollParent(document.getElementById("spanEntity"));
      if (this.scroll) {
        this.scroll.addEventListener("scroll", this.getPosition);
      }
    });
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
  align-items: center;
  flex-shrink: 0;
  min-width: $base-space * 2;
  max-width: v-bind(entityWidth);
  margin-top: -1px;
  text-transform: uppercase;
  font-family: $tertiary-font-family;
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
    position: absolute;
    pointer-events: none;
  }
  &__container {
    position: absolute;
    display: flex;
    margin-top: 20px;
    line-height: 1.2;
    @include font-size(11px);
    pointer-events: all;
  }
  &__score {
    display: inline-flex;
    flex-shrink: 0;
    margin-right: calc($base-space / 2);
  }
  &__text {
    margin-inline: calc($base-space / 4);
    @include truncate(auto);
    @include font-size(0px);
    span {
      @include font-size(11px);
    }
  }
  &__line {
    position: absolute;
    height: 2px;
    background: v-bind(entityColor);
    margin-top: 20px;
    [data-theme="dark"] & {
      background: v-bind("entityColor.palette.veryDark");
    }
  }
  &__suggestion {
    margin-right: calc($base-space / 2);
    flex-shrink: 0;
    &--score {
      display: none;
      margin-right: calc($base-space / 2);
      flex-shrink: 0;
    }
  }
  &:hover {
    position: fixed;
    left: v-bind("entityFixedPosition.left");
    top: v-bind("entityFixedPosition.top");
    z-index: 1;
    transition: scale 0.2s;
    max-width: none;
    scale: 1.1;
    #{$this}__close-button {
      display: inline-flex;
    }
    #{$this}__text {
      min-width: $base-space * 3;
      max-width: none !important;
    }
    #{$this}__score {
      display: inline-flex;
    }
    #{$this}__suggestion {
      &--score {
        display: inline-flex;
      }
    }
    &:before {
      background: v-bind("selectedOption.color");
      width: 100%;
      transition: width 0.2s ease;
      [data-theme="dark"] & {
        background: v-bind("entityColor.palette.veryDark");
      }
    }
  }
  &__close-button {
    display: none;
    padding: 1px;
    border-radius: 0;
    background: var(--color-dark-grey);
    &:hover {
      background: hsl(from var(--color-dark-grey) h s l / 80%);
    }
    [data-theme="dark"] & {
      background: transparent;
      :deep(*) {
        fill: var(--color-white);
      }
      &:hover {
        opacity: 0.8;
      }
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
    [data-theme="dark"] & {
      background: v-bind("entityColor.palette.veryDark");
    }
  }
}
</style>
