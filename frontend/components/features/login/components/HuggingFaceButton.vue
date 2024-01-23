<template>
  <button @click="$emit('click')">
    <img src="./hf-sign-in.svg" draggable="false" />
  </button>
</template>
<script>
export default {
  name: "HuggingFaceButton",
};
</script>

<style lang="scss" scoped>
button {
  border: 0;
  background: none;
  width: 100%;
  user-select: none;
  cursor: pointer;
}
</style>
