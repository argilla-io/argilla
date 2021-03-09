import Component from './Component.vue';
import Api from './api';

const Plugin = (Vue, options = {}) => {
  const methods = Api(Vue, options);
  Vue.$toast = methods;
  Vue.prototype.$toast = methods;
};

Component.install = Plugin;

export default Component;
