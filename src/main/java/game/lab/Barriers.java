package game.lab;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;

/**
 * Turns barriers and latches into {@link Runnable} hooks for tests.
 */
public final class Barriers {

    private Barriers() {
    }

    public static Runnable arrive(CyclicBarrier barrier) {
        return new Runnable() {
            @Override
            public void run() {
                try {
                    barrier.await();
                } catch (Exception ex) {
                    throw new IllegalStateException(ex);
                }
            }
        };
    }

    public static Runnable countDown(CountDownLatch latch) {
        return new Runnable() {
            @Override
            public void run() {
                latch.countDown();
            }
        };
    }
}
