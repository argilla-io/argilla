<template>
  <div class="title-area --body1">
    <span
      class="suggestion-info"
      v-text="question.title"
      v-required-field="{ show: question.isRequired, color: '#cf3832' }"
    />
    <BaseIconWithBadge
      class="icon-info"
      v-if="showIcon"
      icon="info"
      :id="`${question.id}QuestionHeader`"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
      v-tooltip="{
        content: tooltipMessage,
        open: openTooltip,
      }"
    />
  </div>
</template>

<script>
import "assets/icons/info";
import "assets/icons/suggestion";

export default {
  name: "QuestionHeader",
  props: {
    question: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      tooltipMessage: this.question.description,
      openTooltip: false,
      timer: null,
    };
  },
  computed: {
    showIcon() {
      return !!this.question.description?.length;
    },
  },
  watch: {
    "question.description"() {
      if (this.timer) clearTimeout(this.timer);
      this.openTooltip = true;
      this.tooltipMessage = this.question.description;

      this.timer = setTimeout(() => {
        this.openTooltip = false;
      }, 2000);
    },
  },
};
</script>

<style lang="scss" scoped>
.title-area {
  color: var(--fg-primary);
  font-weight: 500;
  &__suggestion-icon {
    cursor: default;
    fill: var(--bg-opacity-54);
  }
}

.icon {
  color: var(--fg-tertiary);
}

.info-icon {
  display: flex;
  flex-basis: 37px;
}

span {
  word-break: break-word;
  line-height: 1.2em;
}

.icon-info {
  display: inline-flex;
  width: 20px;
  height: 20px;
  margin: 0;
  padding: 0;
  vertical-align: middle;
  &[data-title] {
    position: relative;
    overflow: visible;
    &:before,
    &:after {
      margin-top: 0;
    }
  }
}
</style>
