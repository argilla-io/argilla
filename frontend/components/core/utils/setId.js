const setId = {
  created() {
    this.setId();
  },
  methods: {
    setId() {
      Object.keys(this.setIdObject).map((objectKey, index) => {
        const value = this.setIdObject[objectKey];
        this.$set(value, "id", index);
      });
    },
  },
};

export default setId;
