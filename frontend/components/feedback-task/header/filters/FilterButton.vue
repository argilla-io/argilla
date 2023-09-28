<template>
  <div :class="isButtonActive ? 'filter-button--active' : 'filter-button'">
    <BaseButton class="filter-button__button" v-if="!badges.length">{{
      buttonName
    }}</BaseButton>
    <svgicon v-else :name="iconName" width="16" height="16" />
    <div class="filter-button__badges" v-if="badges.length">
      <FilterBadge
        class="filter-button__badge"
        :active-badge="activeBadge === badge && isActive"
        v-for="(badge, index) in visibleBadges"
        :key="badge"
        :text="`${badge} ${
          badgesCustomText.length ? badgesCustomText[index] : ''
        }`"
        @on-click="clickable ? onClickOnBadge(badge, $event) : null"
        @on-clear="onClickOnClear(badge, $event)"
      ></FilterBadge>
      <div
        class="filter-button__badges__collapsed"
        v-if="badges.length > maxVisibleBadges"
        v-click-outside="{
          events: ['mousedown'],
          handler: onClickOutside,
        }"
      >
        <BaseBadge
          :text="`${collapsedBadgeText} ${badges.length - maxVisibleBadges}`"
          @on-click="toggleTooltip"
        />
        <FilterTooltip v-if="visibleTooltip" class="metadata-button__tooltip">
          <FilterBadge
            class="badge"
            v-for="(badge, index) in collapsedBadges"
            :key="badge"
            :text="`${badge} ${
              badgesCustomText.length ? badgesCustomText[index] : ''
            }`"
            @on-click="
              clickable ? onClickOnBadge(badge, $event) : onClickOutside($event)
            "
            @on-clear="onClickOnClear(badge, $event)"
          ></FilterBadge>
        </FilterTooltip>
      </div>
    </div>
    <svgicon
      class="filter-button__chevron"
      name="chevron-down"
      width="16"
      height="16"
    />
  </div>
</template>

<script>
import "assets/icons/chevron-down";
import "assets/icons/filter";
import "assets/icons/sort";
export default {
  props: {
    buttonName: {
      type: String,
      required: true,
    },
    iconName: {
      type: String,
      required: true,
    },
    badges: {
      type: Array,
      default: () => [],
    },
    badgesCustomText: {
      type: Array,
      default: () => [],
    },
    collapsedBadgeText: {
      type: String,
      default: "+",
    },
    activeBadge: {
      type: String,
    },
    maxVisibleBadges: {
      default: 2,
    },
    isActive: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      visibleTooltip: false,
      clickable: false,
    };
  },
  computed: {
    visibleBadges() {
      return this.badges.slice(0, this.maxVisibleBadges);
    },
    collapsedBadges() {
      return this.badges.slice(this.maxVisibleBadges, this.badges.length);
    },
    isButtonActive() {
      return this.isActive || !!this.badges.length;
    },
  },
  methods: {
    onClickOnBadge(badge, e) {
      e.stopPropagation();

      this.$emit("click-on-badge", badge, e);
    },
    onClickOnClear(badge, e) {
      e.stopPropagation();

      this.$emit("click-on-clear", badge, e);
    },
    toggleTooltip(e) {
      e.stopPropagation();
      this.visibleTooltip = !this.visibleTooltip;
    },
    onClickOutside() {
      this.visibleTooltip = false;
    },
  },
  mounted() {
    if (this.$listeners["click-on-badge"]) {
      this.clickable = true;
    }
  },
};
</script>

<styles lang="scss" scoped>
.filter-button {
  display: flex;
  gap: $base-space;
  align-items: center;
  height: $base-space * 5;
  padding: $base-space $base-space * 2;
  border-radius: $border-radius;
  background: none;
  transition: background-color 0.2s ease;
  cursor: pointer;
  &:hover,
  &--active {
    background: $black-4;
    @extend .filter-button;
  }
  &--active {
    &:hover {
      background: $black-6;
    }
  }
  &__badges {
    display: flex;
    gap: calc($base-space / 2);
    &__collapsed {
      position: relative;
    }
  }
  &__badge :deep(.badge__text) {
    max-width: 140px;
  }
  &__button.button {
    padding: 0;
    border-radius: 0;
  }
  &__tooltip {
    display: flex;
    flex-direction: column;
    gap: calc($base-space / 2);
    .badge {
      margin-right: auto;
    }
  }
}
</styles>
