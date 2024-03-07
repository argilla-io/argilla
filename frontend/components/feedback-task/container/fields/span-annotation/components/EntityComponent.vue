<template>
  <div
    class="span-entity__wrapper"
    :style="{ left: entityPosition.left, top: entityPosition.top }"
    ref="spanEntityRef"
    id="spanEntity"
  >
    <div @click="toggleDropdown()" class="span-entity" v-if="!visibleDropdown">
      {{ selectedOption.text }}
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
  display: flex;
  gap: 2px;
  margin-top: -1px;
  max-width: v-bind("entityPosition.width");
  min-width: 10px;
  text-transform: uppercase;
  font-family: "Roboto Condensed", sans-serif;
  cursor: pointer;
  @include truncate;
  transition: background 0.3s;
  &__wrapper {
    position: absolute;
    display: block;
    margin-top: 20px;
    line-height: 1.2;
    @include font-size(11px);
  }
  &:hover {
    position: relative;
    max-width: none;
    z-index: 1;
    background: v-bind("selectedOption.color");
    transition: background 0.3s;

    > button {
      opacity: 1;
    }
  }
  &__close-button {
    opacity: 0;
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
}
</style>
