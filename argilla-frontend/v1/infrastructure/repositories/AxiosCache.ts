const threeSecondsOfCache = 3;
const oneSecond = 1000;

export const getCacheKey = (config) => {
  if (!config.params) return `${config.method}-${config.url}`;

  return `${config.method}-${config.url}-${JSON.stringify(config.params)}`;
};

export const revalidateCache = (key: string) => {
  const internalKey = `get-${key}`;

  if (!cache.has(internalKey)) return;

  cache.delete(internalKey);
};

type Cache = {
  items: Record<string, any>;
  has: (key: string) => boolean;
  get: (key: string) => any;
  set: (key: string, value: any, secondsDefined: string) => void;
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
  set(key, value, secondsDefined) {
    if (this.has(key)) return;

    this.items[key] = value;

    const seconds = secondsDefined
      ? parseInt(secondsDefined)
      : threeSecondsOfCache;

    setTimeout(() => {
      this.delete(key);
    }, seconds * oneSecond);
  },
  delete(key) {
    delete this.items[key];
  },
};

export const loadCache = (axios) => {
  axios.interceptors.request.use((request) => {
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

  axios.interceptors.response.use((response) => {
    if (response.config.method === "get") {
      if (!response.config.headers["cache-control"]) return response;

      const seconds = response.config.headers["cache-control"]
        .replace("max-age", "")
        .replace("=", "");

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

export const largeCache = () => {
  return {
    headers: { "cache-control": "max-age=600" },
  };
};

export const mediumCache = () => {
  return {
    headers: { "cache-control": "max-age=120" },
  };
};
