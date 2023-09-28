export interface Response<T> {
  items: T;
}

export interface ResponseWithTotal<T> extends Response<T> {
  total: number;
}
