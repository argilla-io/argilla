<template>
  <div class="chat" :key="title">
    <span class="chat__title" v-text="title" />
    <div
      class="chat__wrapper"
      :class="checkIfAreLessThanTwoRoles ? '--simple' : '--multiple'"
    >
      <div
        :id="`fields-content-${name}`"
        v-for="({ role, content: text }, index) in content"
        :key="index"
      >
        <span
          :class="[
            'chat__item',
            checkIfAreLessThanTwoRoles && index % 2 == 0
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
            <span v-else v-html="text" /><template>
              <style :key="name" scoped>
                ::highlight(search-text-highlight-{{name}}) {
                  color: #ff675f;
                }
              </style>
            </template>
          </div>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { useChatFieldViewModel } from "./useChatFieldViewModel";
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
    searchText: {
      type: String,
      default: "",
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
        "var(--fg-chat-1)",
        "var(--fg-chat-2)",
        "var(--fg-chat-3)",
        "var(--fg-chat-4)",
        "var(--fg-chat-5)",
      ];
    },
  },
  methods: {
    getColorForRole(role) {
      return this.colorForRole[this.getAllUniqueRolesNames.indexOf(role)];
    },
  },
  setup(props) {
    return useChatFieldViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.chat {
  $this: &;
  margin-bottom: $base-space * 3;
  &__wrapper {
    display: flex;
    flex-direction: column;
    gap: $base-space + calc($base-space / 2);
    padding: 0 $base-space * 2;
  }
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
    &:has(p) {
      padding: 2 * $base-space 2 * $base-space $base-space 2 * $base-space;
    }
    .--simple & {
      border-color: var(--border-field) !important;
    }
    .--multiple & {
      max-width: 100%;
    }
  }

  &__role {
    font-weight: 500;
    @include font-size(13px);
  }

  &__title {
    display: inline-block;
    word-break: break-word;
    width: calc(100% - 30px);
    margin-bottom: $base-space * 2;
    color: var(--fg-secondary);
  }
}
</style>
