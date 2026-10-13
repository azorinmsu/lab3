package game.loop;

/**
 * Pause / resume gate for the game clock.
 * After a confirmed pause, ticks must not run until resume.
 */
public class PauseController {

    private boolean paused;
    private int ticks;
    private volatile Runnable beforeTickDecision;
    private volatile Runnable beforePause;

    public void setBeforeTickDecision(Runnable beforeTickDecision) {
        this.beforeTickDecision = beforeTickDecision;
    }

    public void setBeforePause(Runnable beforePause) {
        this.beforePause = beforePause;
    }

    public void pause() {
        Runnable hook = beforePause;
        if (hook != null) {
            hook.run();
        }
        paused = true;
    }

    public void resume() {
        paused = false;
    }

    public boolean isPaused() {
        return paused;
    }

    public int getTicks() {
        return ticks;
    }

    /**
     * Attempts one game tick. Returns whether the tick actually ran.
     */
    public boolean tryTick() {
        boolean observedPaused = paused;
        Runnable hook = beforeTickDecision;
        if (hook != null) {
            hook.run();
        }
        if (observedPaused) {
            return false;
        }
        ticks++;
        return true;
    }
}
