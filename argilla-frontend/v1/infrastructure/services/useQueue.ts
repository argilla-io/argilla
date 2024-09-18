class Routine {
  constructor(private readonly executable: Function) {}

  execute() {
    return this.executable();
  }
}

class Queue {
  private readonly queue: Routine[] = [];

  async enqueue(element: Function) {
    const routine = new Routine(element);
    this.queue.push(routine);

    await this.tryExecution();
  }

  private async tryExecution() {
    if (this.size > 1) return;

    while (!this.isEmpty) {
      const routine = this.peek();

      await routine.execute();

      this.dequeue();
    }
  }

  private peek(): Routine {
    return this.queue[0];
  }

  private get isEmpty(): boolean {
    return this.size === 0;
  }

  private get size(): number {
    return this.queue.length;
  }

  private dequeue() {
    this.queue.shift();
  }
}

export const useQueue = () => {
  return new Queue();
};
