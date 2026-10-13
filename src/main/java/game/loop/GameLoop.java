package game.loop;

import java.util.concurrent.atomic.AtomicInteger;

/**
 * Background game loop. {@link #stop()} must make {@link #run()} exit.
 * Stale local sampling of {@code running} is the intentional defect.
 */
public class GameLoop {

    private boolean running;
    private final AtomicInteger ticks = new AtomicInteger();
    private volatile Runnable afterTick;

    public void setAfterTick(Runnable afterTick) {
        this.afterTick = afterTick;
    }

    public void startFlag() {
        running = true;
    }

    public void stop() {
        running = false;
    }

    public boolean isRunning() {
        return running;
    }

    public int getTicks() {
        return ticks.get();
    }

    /**
     * Runs until stop is observed. The buggy version samples {@code running} once.
     */
    public void run() {
        boolean keepGoing = running;
        while (keepGoing) {
            ticks.incrementAndGet();
            Runnable hook = afterTick;
            if (hook != null) {
                hook.run();
            }
            // Missing re-read of running → stop() stays invisible to this loop.
        }
    }
}
