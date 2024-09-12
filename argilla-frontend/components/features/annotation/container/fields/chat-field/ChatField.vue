<template>
  <div
    class="chat"
    :key="title"
    :class="checkIfAreLessThanTwoRoles ? '--simple' : '--multiple'"
  >
    <span class="chat__title" v-text="title" />

    <div v-for="({ role, content: text }, index) in content" :key="index">
      <span
        :class="[
          'chat__item',
          checkIfAreLessThanTwoRoles && index === 0
            ? 'chat__item--right'
            : 'chat__item--left',
        ]"
      >
        <span
          class="chat__role"
          v-if="role !== content[index - 1]?.role"
          v-text="role"
          :style="{
            color: getColorForRole(role),
          }"
        />

        <div
          class="chat__bubble"
          :style="{
            borderColor: `hsl(from ${getColorForRole(role)} h s l / 20%)`,
          }"
        >
          <MarkdownRenderer v-if="useMarkdown" :markdown="text" />
          <span v-else v-html="text" />
        </div>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    name: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    content: {
      type: Array,
      required: true,
    },
    useMarkdown: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    getAllUniqueRolesNames() {
      return this.content
        .map((item) => item.role)
        .filter((role, index, self) => self.indexOf(role) === index);
    },
    checkIfAreLessThanTwoRoles() {
      return this.getAllUniqueRolesNames.length <= 2;
    },
    colorForRole() {
      return [
        "hsl(117, 30%, 58%)",
        "hsl(288, 30%, 58%)",
        "hsl(189, 30%, 58%)",
        "hsl(0, 30%, 58%)",
        "hsl(50, 30%, 58%)",
      ];
    },
  },
  methods: {
    getColorForRole(role) {
      return this.colorForRole[this.getAllUniqueRolesNames.indexOf(role)];
    },
  },
};
</script>

<style lang="scss" scoped>
.chat {
  $this: &;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  margin-bottom: $base-space * 3;
  &__item {
    display: flex;
    flex-direction: column;
    gap: calc($base-space / 2);
    &--right {
      align-items: flex-end;
      align-self: flex-end;
      #{$this}__bubble {
        background: var(--bg-bubble-inverse);
        border-top-right-radius: 3px;
      }
    }

    &--left {
      align-items: flex-start;
      align-self: flex-start;
      #{$this}__bubble {
        background: var(--bg-bubble);
        border-top-left-radius: 3px;
      }
    }
  }

  &__bubble {
    max-width: 80%;
    padding: 2 * $base-space;
    border-radius: $border-radius-l;
    border-style: solid;
    border-width: 1px;
    @include font-size(16px);
    @include line-height(24px);
    white-space: pre-wrap;
    word-break: break-word;
    .--simple & {
      border-color: var(--bg-opacity-2) !important;
    }
  }

  &__role {
    font-weight: 600;
  }

  &__title {
    word-break: break-word;
    width: calc(100% - 30px);
    margin-bottom: $base-space * 3;
  }
}
</style>
