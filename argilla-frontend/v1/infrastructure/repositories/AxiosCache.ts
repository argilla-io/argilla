const threeSecondsOfCache = 3;
const oneSecond = 1000;
const cacheControlHeader = "cache-control";
const cacheRevalidateHeader = "must-revalidate";

export const getCacheKey = (config) => {
  if (!config.params) return `${config.method}-${config.url}`;

  return `${config.method}-${config.url}-${JSON.stringify(config.params)}`;
};

export const revalidateCache = (key: string) => {
  const internalKey = `get-${key}`;

  if (!cache.has(internalKey)) return;

  cache.delete(internalKey);
};

const getCachedSeconds = (response: any) => {
  const getSeconds = (secondsFromMaxAge: string) =>
    secondsFromMaxAge.replace("max-age", "").replace("=", "");

  if (response.config.headers[cacheRevalidateHeader])
    return getSeconds(response.config.headers[cacheRevalidateHeader]);

  return getSeconds(response.config.headers[cacheControlHeader]);
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

      if (request.headers[cacheControlHeader]) {
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
        } else {
          request.headers[cacheRevalidateHeader] =
            request.headers[cacheControlHeader];

          request.headers[cacheControlHeader] = cacheRevalidateHeader;
        }
      }
    }

    return request;
  });

  axios.interceptors.response.use((response) => {
    if (response.config.method === "get") {
      if (!response.config.headers[cacheControlHeader]) return response;

      const seconds = getCachedSeconds(response);
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
