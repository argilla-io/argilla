<template>
  <div class="draggable">
    <draggable
      class="draggable__questions-container"
      :list="ranking.questions"
      :group="{ name: 'question' }"
      :sort="false"
      role="listbox"
      aria-orientation="vertical"
    >
      <div
        v-for="item in ranking.questions"
        :id="item.value"
        :key="item.value"
        :title="item.text"
        tabindex="0"
        ref="questions"
        @keydown="rankWithKeyboard($event, item)"
        @focus="onFocus"
      >
        <BaseTooltip
          class="draggable__rank-card--unranked"
          :title="isSuggested(item) ? $t('suggestion.name') : null"
          :text="getSuggestedAgent(item)"
          minimalist
        >
          <svgicon width="6" name="draggable" :id="`${item.value}-icon`" aria-label="Dragging Icon"/>
          <span
            class="draggable__rank-card__title"
            v-text="item.text"
            :id="`${item.value}-span`"
          />

          <span v-if="isSuggested(item)" class="draggable__suggestion">
            <span v-text="getSuggestedRank(item)" />
            <svgicon name="suggestion" width="10" height="10" />
            <span
              class="draggable__suggestion__score"
              v-if="getSuggestedScore(item)"
              v-text="getSuggestedScore(item)"
            />
          </span>
        </BaseTooltip>
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
            :title="item.text"
            tabindex="0"
            ref="items"
            @keydown="rankWithKeyboard($event, item)"
            @focus="onFocus"
          >
            <BaseTooltip
              :title="isSuggested(item) ? $t('suggestion.name') : null"
              :text="getSuggestedAgent(item)"
              minimalist
              class="draggable__rank-card--ranked"
            >
              <svgicon width="6" name="draggable" :id="`${item.value}-icon`" />
              <span
                class="draggable__rank-card__title"
                v-text="item.text"
                :id="`${item.value}-span`"
              />

              <span v-if="isSuggested(item)" class="draggable__suggestion">
                <span v-text="getSuggestedRank(item)" />
                <svgicon name="suggestion" width="10" height="10" />
                <span
                  class="draggable__suggestion__score"
                  v-if="getSuggestedScore(item)"
                  v-text="getSuggestedScore(item)"
                />
              </span>
            </BaseTooltip>
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
    suggestion: {
      type: Object,
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
    isSuggested(item) {
      return this.suggestion?.isSuggested(item);
    },
    getSuggestedAgent(item) {
      return this.suggestion?.getSuggestion(item)?.agent;
    },
    getSuggestedScore(item) {
      return this.suggestion?.getSuggestion(item)?.score?.fixed;
    },
    getSuggestedRank(item) {
      return this.suggestion?.getSuggestion(item)?.value.rank;
    },
  },
};
</script>

<style lang="scss" scoped>
$card-bg-primary-color: var(--bg-label);
$card-primary-color: var(--fg-label-2);
$card-bg-secondary-color: var(--bg-accent-grey-2);
$cards-separation: $base-space;
$background-slot-color: var(--bg-opacity-4);
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

    &.ghost-ticket {
      box-shadow: none;
    }
    &.sortable-ghost {
      box-shadow: none;
      &:hover {
        box-shadow: none;
      }
    }
    &--unranked {
      @extend .draggable__rank-card;
      background-color: $card-bg-secondary-color;
      color: $card-primary-color;
      transition: box-shadow 0.2s ease-out !important;

      &:focus {
        outline: 2px solid var(--fg-cuaternary) !important;
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
      background-color: $card-bg-primary-color;
      color: var(--color-white);
      &:focus {
        outline: 2px solid var(--fg-cuaternary);
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
    width: calc(100% - $base-space * 7);
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
        border: 1px dashed var(--bg-opacity-10);
      }
    }
    &--ranking {
      @extend .draggable__slot-box;
      flex-shrink: 0;
      max-width: $slot-height;
      align-items: center;
      justify-content: space-around;
      border-color: var(--bg-opacity-10);
      font-weight: bold;
      color: var(--fg-secondary);
      .--active-slot & {
        border-color: hsl(from var(--fg-label) h s l / 30%);
      }
    }
  }

  &__suggestion {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: calc($base-space / 2);
    justify-content: center;
    flex-shrink: 0;
    margin-left: auto;
    @include font-size(13px);
    cursor: default;
    &__score {
      @include font-size(11px);
    }
  }

  [draggable="true"] {
    :deep(.tooltip-content) {
      display: none;
    }
  }

  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
