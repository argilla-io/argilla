def start_loop_in_thread():
    """Launches a asyncio loop in a different thread and start it"""
    from threading import Thread
    import asyncio

    def start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    new_loop = asyncio.new_event_loop()
    t = Thread(target=start_loop, args=(new_loop,), daemon=True)
    t.start()

    return new_loop
