import { useQueue } from "./useQueue";

describe("Queue should", () => {
  test("execute each element in a queue synchronously", (done) => {
    let current = 0;
    const queue = useQueue();

    const firstCall = async () => {
      expect(current).toBe(0);

      await new Promise((resolve) =>
        setTimeout(() => {
          current++;

          resolve(current);
        }, 100)
      );

      expect(current).toBe(1);
    };

    const secondCall = async () => {
      expect(current).toBe(1);

      await new Promise((resolve) =>
        setTimeout(() => {
          current++;

          resolve(current);
        }, 10)
      );

      expect(current).toBe(2);

      done();
    };

    queue.enqueue(() => firstCall());

    queue.enqueue(() => secondCall());
  });
});
