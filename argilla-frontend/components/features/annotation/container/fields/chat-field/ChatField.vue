<template>
  <div class="chat-field" :key="fieldText">
    <span class="chat-field_title" v-text="title" />

    <div class="container" v-for="{ role, content } in content">
      <span :class="['message', role === 'user' ? 'user' : 'agent']">
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
}

.container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.user {
  align-items: flex-end;
  background-color: #f5f5f5;
}

.agent {
  background-color: #c2e3f7;
  align-items: flex-start;
}

.message {
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
</style>
