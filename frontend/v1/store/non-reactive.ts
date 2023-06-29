const hydrate = (base: any, data: any) => {
  Object.entries(data).forEach((entry) => {
    if (typeof entry[1] === "object" && !!base[entry[0]]) {
      const inner = base[entry[0]];

      base[entry[0]] = hydrate(inner, entry[1]);
    } else {
      base[entry[0]] = entry[1];
    }
  });

  return base;
};

export const create = <T>(Ctor: any, data: any): T => {
  const base = new Ctor() as T;

  hydrate(base, data);

  return base;
};
