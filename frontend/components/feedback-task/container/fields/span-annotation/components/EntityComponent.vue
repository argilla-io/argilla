<template>
  <div
    class="span-entity__wrapper"
    :style="{ left: entityPosition.left, top: entityPosition.top }"
    ref="spanEntityRef"
    id="spanEntity"
  >
    <div
      v-on="!singleOption ? { click: toggleDropdown } : {}"
      :class="!singleOption ? 'span-entity--clickable' : 'span-entity'"
      v-if="!visibleDropdown"
    >
      <svgicon
        v-if="suggestionScore"
        class="span-entity__suggestion"
        name="suggestion"
        width="8"
        height="8"
      />
      <span class="span-entity__text" v-text="selectedOption.text" />
      <span
        v-if="suggestionScore"
        class="span-entity__score"
        v-text="suggestionScore"
      />
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
    </div>
    <EntityComponentDropdown
      v-else
      :style="{
        left: spanEntityPosition.left,
        top: spanEntityPosition.top,
      }"
      :selectedOption="selectedOption"
      :options="options"
      @on-replace-option="selectOption"
      @on-remove-option="removeSelectedOption"
      v-click-outside="hideDropdown"
    />
  </div>
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
      return this.suggestion?.score.toFixed(1);
    },
  },
  methods: {
    selectOption(option) {
      this.$emit("on-replace-option", option);
      this.hideDropdown();
    },
    removeSelectedOption() {
      this.$emit("on-remove-option");
      this.hideDropdown();
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
      this.spanEntityPosition.left = `${position.left}px`;
      this.spanEntityPosition.top = `${
        position.top + this.$refs.spanEntityRef.scrollTop
      }px`;
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
  text-transform: uppercase;
  font-family: "Roboto Condensed", sans-serif;
  user-select: none;
  transition: background 0.3s;
  &__wrapper {
    position: absolute;
    display: flex;
    margin-top: 20px;
    line-height: 1.2;
    @include font-size(11px);
  }
  &__score {
    display: none;
  }
  &__text {
    gap: 4px;
    @include truncate(auto);
  }
  &:hover {
    position: relative;
    z-index: 1;
    background: v-bind("selectedOption.color");
    transition: background 0.3s;
    max-width: none;

    #{$this}__close-button {
      display: inline-flex;
    }
    #{$this}__score {
      display: inline-flex;
    }
  }
  &__close-button {
    display: none;
    padding: 0;
    flex-shrink: 0;
    border-radius: 0;
    &__icon {
      min-width: 10px;
      color: $black-54;
      &:hover {
        color: $black-87;
      }
    }
  }
  &--clickable {
    cursor: pointer;
    @extend .span-entity;
  }
}
</style>
