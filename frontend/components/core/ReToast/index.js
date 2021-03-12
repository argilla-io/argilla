import Toast from './Toast.vue';
import Api from './api';

const Plugin = (Vue, options = {}) => {
  const methods = Api(Vue, options);
  Vue.$toast = methods;
  Vue.prototype.$toast = methods;
};

Toast.install = Plugin;

export default Toast;
