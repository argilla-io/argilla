const threeSecondsOfCache = 3;

const getCacheKey = (config) => {
  if (!config.params) return `${config.method}-${config.url}`;

  return `${config.method}-${config.url}-${JSON.stringify(config.params)}`;
};

type Cache = {
  items: Record<string, any>;
  has: (key: string) => boolean;
  get: (key: string) => any;
  set: (key: string, value: any, seconds: number) => void;
  delete: (key: string) => void;
};

const cache: Cache = {
  items: {},
  has(key) {
    return !!this.items[key];
  },
  get(key) {
    if (!this.has(key)) return;

    return this.items[key];
  },
  set(key, value, seconds) {
    if (this.has(key)) return;

    this.items[key] = value;

    setTimeout(() => {
      this.delete(key);
    }, seconds * 1000);
  },
  delete(key) {
    delete this.items[key];
  },
};

export default ({ $axios }) => {
  $axios.interceptors.request.use((request) => {
    if (request.method === "get") {
      const key = getCacheKey(request);

      if (cache.has(key)) {
        const { data, headers } = cache.get(key);

        request.data = data;

        request.adapter = () =>
          Promise.resolve({
            data,
            status: request.status,
            statusText: request.statusText,
            headers,
            config: request,
            request,
          });
      }
    }

    return request;
  });

  $axios.interceptors.response.use((response) => {
    if (response.config.method === "get") {
      if (!response.config.headers["cache-control"]) return response;

      const userSecondsDefined = response.config.headers["cache-control"]
        .replace("max-age", "")
        .replace("=", "");

      const seconds = userSecondsDefined
        ? parseInt(userSecondsDefined)
        : threeSecondsOfCache;

      const key = getCacheKey(response.config);
      cache.set(
        key,
        { data: response.data, headers: response.headers },
        seconds
      );
    }

    return response;
  });
};
