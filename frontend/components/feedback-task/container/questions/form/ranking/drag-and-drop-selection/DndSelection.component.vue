<template>
  <div class="draggable">
    <draggable
      class="draggable__questions-container"
      :list="ranking.questions"
      :group="{ name: 'question' }"
      :sort="false"
    >
      <div
        v-for="item in ranking.questions"
        :id="item.value"
        :key="item.value"
        class="draggable__rank-card--unranked"
        :title="item.text"
        tabindex="0"
        ref="questions"
        @keydown="rankWithKeyboard($event, item)"
        @focus="onFocus"
      >
        <svgicon width="6" name="draggable" :id="`${item.value}-icon`" />
        <span
          class="draggable__rank-card__title"
          v-text="item.text"
          :id="`${item.value}-span`"
        />
        <span
          :title="$t('suggestion.suggested-rank')"
          class="draggable__suggestion"
          v-if="findRankSuggestion(item.value)"
          >{{ findRankSuggestion(item.value).rank }}</span
        >
      </div>
    </draggable>

    <div class="draggable__slots-container">
      <div
        class="draggable__slot"
        :class="{ '--active-slot': items.length }"
        v-for="{ index, rank, items } in ranking.slots"
        :key="index"
      >
        <span class="draggable__slot-box--ranking" v-text="rank" />
        <draggable
          class="draggable__slot-box"
          :list="items"
          group="question"
          :sort="false"
          @add="onMoveEnd"
          @remove="onMoveEnd"
        >
          <div
            v-for="item in items"
            :id="item.value"
            :key="item.value"
            class="draggable__rank-card--ranked"
            :title="item.text"
            tabindex="0"
            ref="items"
            @keydown="rankWithKeyboard($event, item)"
            @focus="onFocus"
          >
            <svgicon width="6" name="draggable" :id="`${item.value}-icon`" />
            <span
              class="draggable__rank-card__title"
              v-text="item.text"
              :id="`${item.value}-span`"
            />
            <span
              :title="$t('suggestion.suggested-rank')"
              class="draggable__suggestion"
              v-if="findRankSuggestion(item.value)"
              >{{ findRankSuggestion(item.value).rank }}</span
            >
          </div>
        </draggable>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/draggable";

export default {
  name: "DndSelectionComponent",
  props: {
    ranking: {
      type: Object,
      required: true,
    },
    suggestions: {
      type: Array,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  data() {
    return {
      timer: null,
      keyCode: "",
    };
  },
  watch: {
    isFocused: {
      immediate: true,
      handler(newValue) {
        const questionsAndItems = [
          ...(this.$refs.questions || []),
          ...(this.$refs.items || []),
        ];

        const componentContainsActiveElement = questionsAndItems?.includes(
          document.activeElement
        );

        if (newValue && !componentContainsActiveElement) {
          this.focusOnFirstQuestionOrItem();
        }
      },
    },
  },
  methods: {
    reset() {
      this.keyCode = "";
      this.timer = null;
    },
    isGlobalShortcut(event) {
      return (
        event.key == "Tab" ||
        event.code === "Enter" ||
        event.code === "Backspace" ||
        event.code === "ArrowLeft" ||
        event.code === "ArrowRight" ||
        event.code === "ArrowUp" ||
        event.code === "ArrowDown"
      );
    },
    rankWithKeyboard(event, questionToMove) {
      if (this.timer) clearTimeout(this.timer);
      if (this.isGlobalShortcut(event)) return;

      event.stopPropagation();

      this.keyCode += event.key;

      if (isNaN(this.keyCode)) {
        this.reset();
        return;
      }

      const slotTo = this.ranking.slots[this.keyCode - 1];

      if (!slotTo) {
        this.reset();
        return;
      }

      this.ranking.moveQuestionToSlot(questionToMove, slotTo);
      this.onMoveEnd();

      this.$nextTick(() => {
        const questionRanked = this.$refs.items?.find(
          ({ title }) => title == questionToMove?.text
        );

        questionRanked?.focus();
      });

      this.timer = setTimeout(() => {
        this.$nextTick(() => {
          this.focusOnFirstQuestionOrItem();
          this.reset();
        });
      }, 300);
    },
    focusOnFirstQuestionOrItem() {
      this.$nextTick(() => {
        const firstQuestion = this.$refs.questions?.find(
          ({ title }) => title == this.ranking.questions[0]?.text
        );

        if (!firstQuestion) {
          const firstItem = this.$refs.items[0];

          firstItem?.focus();

          return;
        }

        firstQuestion.focus();
      });
    },
    onMoveEnd() {
      this.$emit("on-reorder", this.ranking);
    },
    onFocus() {
      this.$emit("on-focus");
    },
    findRankSuggestion(value) {
      return this.suggestions?.find((suggestion) => suggestion.value == value);
    },
  },
};
</script>

<style lang="scss" scoped>
$card-primary-color: palette(purple, 200);
$card-secondary-color: palette(white);
$card-ghost-color: palette(purple, 300);
$card-empty-color: palette(purple, 400);
$suggestion-color: palette(yellow, 400);
$cards-separation: $base-space;
$background-slot-color: $black-4;
$slot-height: 50px;
$card-height: $base-space * 4;
$max-visible-card-items: 12;

.draggable {
  user-select: none;
  display: flex;
  flex-direction: row-reverse;
  gap: $base-space;
  &__questions-container {
    display: flex;
    flex-direction: column;
    gap: $cards-separation;
    width: 40%;
    min-width: 0;
    max-height: ($card-height + $base-space) * $max-visible-card-items;
    padding: 2px;
    overflow: auto;
  }

  &__slots-container {
    width: 60%;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: $cards-separation;
  }

  &__slot {
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: stretch;
    justify-items: center;
    gap: $base-space;
  }

  &__rank-card {
    height: $card-height;
    min-width: 50px;
    display: flex;
    align-items: center;
    gap: $base-space;
    padding: $base-space;
    border-radius: $border-radius;
    cursor: move;

    &[draggable="true"] {
      background: $card-ghost-color;
      color: $card-primary-color;
      box-shadow: $shadow-500;
      &:focus {
        outline: none !important;
      }
    }
    &.ghost-ticket {
      background: $card-empty-color;
      color: $card-empty-color;
      box-shadow: none;
    }
    &.sortable-ghost {
      background: $card-empty-color;
      color: $card-empty-color;
      box-shadow: none;
      &:hover {
        box-shadow: none;
      }
    }
    &--unranked {
      @extend .draggable__rank-card;
      background-color: $card-secondary-color;
      color: $card-primary-color;
      transition: box-shadow 0.2s ease-out !important;

      &:focus {
        outline: 2px solid $primary-color !important;
      }
      &:focus:not(:focus-visible) {
        outline: none;
      }
      &:hover {
        box-shadow: $shadow-100;
        transition: box-shadow 0.2s ease-in;
      }
    }
    &--ranked {
      @extend .draggable__rank-card;
      background-color: $card-primary-color;
      color: palette(white);
      &:focus {
        outline: 2px solid $primary-color;
      }
      &:focus:not(:focus-visible) {
        outline: none;
      }
    }
    &__title {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 500;
    }
  }

  &__slot-box {
    width: calc(100% - $base-space * 6);
    min-height: $slot-height;
    display: flex;
    flex-direction: column;
    gap: calc($base-space / 2);
    padding: $base-space;
    background-color: $background-slot-color;
    border-radius: $border-radius;
    border: 1px solid transparent;
    @supports (selector(:has(*))) {
      &:has([draggable="true"]) {
        border: 1px dashed $black-10;
      }
    }
    &--ranking {
      @extend .draggable__slot-box;
      flex-shrink: 0;
      max-width: $slot-height;
      align-items: center;
      justify-content: space-around;
      border-color: $black-10;
      font-weight: bold;
      color: $black-54;
      .--active-slot & {
        border-color: #cdcdff;
      }
    }
  }

  &__suggestion {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    height: $base-space * 2;
    width: $base-space * 2;
    margin-left: auto;
    border-radius: $border-radius-rounded;
    border: 1px solid $suggestion-color;
    color: $card-primary-color;
    background: $suggestion-color;
    @include font-size(12px);
    cursor: default;
  }

  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
