<template>
  <div class="chat-field" :key="fieldText">
    <span class="chat-field_title" v-text="title" />

    <div
      class="chat-field_container"
      v-for="({ role, content }, index) in content"
      :key="index"
    >
      <span
        :class="[
          'chat-field_message',
          role === 'user' ? 'chat-field_user' : 'chat-field_agent',
        ]"
        :style="{
          backgroundColor: $color.generate(role).palette.light,
        }"
      >
        <span v-text="role" />

        <p v-text="content" />
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
  },
};
</script>

<style lang="scss" scoped>
.chat-field {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius-m;

  &_title {
    color: $black-87;
    word-break: break-word;
    width: calc(100% - 30px);
  }

  &_container {
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  &_user {
    background-color: #f5f5f5;
    align-items: flex-end;
    align-self: flex-end;
  }

  &_agent {
    background-color: #c2e3f7;
    align-items: flex-start;
    align-self: flex-start;
  }

  &_message {
    & > span {
      font-weight: bold;
    }

    display: flex;
    flex-direction: column;
    width: fit-content;
    max-width: 80%;
    border-radius: 10px;
    padding: 10px;
  }
}
</style>
