package game.loop;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Starts and stops the background game task.
 */
public class GameService {

    private final AtomicInteger activeTasks = new AtomicInteger();
    private ExecutorService executor;
    private volatile boolean stopRequested;
    private volatile Runnable beforeTaskBody;

    public void setBeforeTaskBody(Runnable beforeTaskBody) {
        this.beforeTaskBody = beforeTaskBody;
    }

    public synchronized void start() {
        stopRequested = false;
        if (executor == null || executor.isShutdown()) {
            executor = Executors.newCachedThreadPool();
        }
        executor.execute(new Runnable() {
            @Override
            public void run() {
                activeTasks.incrementAndGet();
                try {
                    Runnable hook = beforeTaskBody;
                    if (hook != null) {
                        hook.run();
                    }
                    // Defect: ignore stopRequested and never exit unless the pool is shut down.
                    while (true) {
                        Thread.yield();
                    }
                } finally {
                    activeTasks.decrementAndGet();
                }
            }
        });
    }

    public synchronized void stop() {
        stopRequested = true;
        // Defect: do not shut down the executor or interrupt running tasks.
    }

    public int getActiveTasks() {
        return activeTasks.get();
    }

    public boolean awaitIdle(long timeoutMillis) throws InterruptedException {
        long deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(timeoutMillis);
        while (activeTasks.get() > 0) {
            if (System.nanoTime() >= deadline) {
                return false;
            }
            Thread.yield();
        }
        return true;
    }
}
