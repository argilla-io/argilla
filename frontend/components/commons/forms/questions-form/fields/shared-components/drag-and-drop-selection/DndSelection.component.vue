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
        :key="item.value"
        class="draggable__rank-card--unranked"
        :title="item.text"
        tabindex="0"
        ref="question"
        @keydown="rankWithKeyboard($event, item)"
        @focus="onFocus"
      >
        <svgicon width="7" name="draggable" />
        <span class="draggable__rank-card__title" v-text="item.text" />
      </div>
    </draggable>

    <div class="draggable__slots-container">
      <div
        class="draggable__slot"
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
            :key="item.value"
            class="draggable__rank-card--ranked"
            :title="item.text"
            tabindex="0"
            ref="items"
            @keydown="rankWithKeyboard($event, item)"
            @focus="onFocus"
          >
            <svgicon width="7" name="draggable" />
            <span class="draggable__rank-card__title" v-text="item.text" />
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
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  watch: {
    isFocused: {
      immediate: true,
      handler(newValue) {
        !!newValue && this.onAutoFocusFirstItem();
      },
    },
  },
  methods: {
    rankWithKeyboard(event, item) {
      const keyCode = event.key;
      const validKeyCodes = [
        { key: "1", rank: 1 },
        { key: "2", rank: 2 },
        { key: "3", rank: 3 },
        { key: "4", rank: 4 },
        { key: "5", rank: 5 },
        { key: "6", rank: 6 },
        { key: "7", rank: 7 },
        { key: "8", rank: 8 },
        { key: "9", rank: 9 },
        { key: "=", rank: 10 },
        { key: "!", rank: 11 },
        { key: '"', rank: 12 },
      ];

      const keysForAvailableRankingSlots = validKeyCodes.slice(
        0,
        this.ranking.slots.length
      );
      const getRankPosition =
        keysForAvailableRankingSlots.find((item) => item.key === keyCode)
          ?.rank || null;
      if (getRankPosition) {
        const slots = this.ranking.slots;
        const questions = this.ranking.questions;
        const getIndexInSlot = this.ranking.slots[
          Number(getRankPosition) - 1
        ].items.findIndex((it) => it.id === item.id);

        const getIndexInQuestions = questions.findIndex(
          (q) => q.id === item.id
        );

        if (getIndexInSlot > -1) {
          return;
        } else {
          if (getIndexInQuestions > -1) {
            questions.splice(getIndexInQuestions, 1);
          } else {
            const getIndexInRanking = slots.findIndex((slot) =>
              slot.items.some((i) => i.id === item.id)
            );
            const getIndexOfElement = slots[getIndexInRanking].items.findIndex(
              (i) => i.id === item.id
            );
            slots[getIndexInRanking].items.splice(getIndexOfElement, 1);
          }
          slots[Number(getRankPosition) - 1].items.push(item);
        }
        this.$emit("on-reorder", this.ranking);
        this.onAutoFocusFirstItem();
      }
    },
    onMoveEnd() {
      this.$emit("on-reorder", this.ranking);
    },
    onFocus() {
      this.$emit("on-focus");
    },
    onAutoFocusFirstItem() {
      this.$nextTick(() => {
        if (this.$refs.question && this.$refs.question[0]) {
          this.$refs.question[0].focus();
        } else {
          this.$refs.items[0].focus();
        }
      });
    },
  },
};
</script>

<style lang="scss" scoped>
$card-primary-color: palette(purple, 200);
$card-secondary-color: palette(white);
$card-ghost-color: palette(purple, 300);
$card-empty-color: palette(purple, 400);
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
    width: 40%;
    min-width: 0;
    max-height: ($card-height + $base-space) * $max-visible-card-items;
    display: flex;
    flex-direction: column;
    gap: $cards-separation;
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
    gap: calc($base-space / 2);
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
      transition: box-shadow 0.2s ease-out;
      &:focus {
        outline: 2px solid $card-primary-color;
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
        outline: 2px solid palette(apricot);
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
      max-width: $base-space * 5;
      align-items: center;
      justify-content: space-around;
      border-color: $black-10;
      font-weight: bold;
      color: $black-54;
    }
  }

  .svg-icon {
    flex-shrink: 0;
  }
}
</style>
