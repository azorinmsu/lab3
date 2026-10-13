package game.score;

/**
 * Running score for a Snake match.
 * {@link #setBeforeUpdate(Runnable)} lets tests align threads.
 * The hook does not change the rule: a successful {@code addPoints(n)} adds exactly n.
 */
public class ScoreCounter {

    private int score;
    private volatile Runnable beforeUpdate;

    public void setBeforeUpdate(Runnable beforeUpdate) {
        this.beforeUpdate = beforeUpdate;
    }

    public void addPoints(int points) {
        if (points <= 0) {
            throw new IllegalArgumentException("points must be positive");
        }
        int observed = score;
        Runnable hook = beforeUpdate;
        if (hook != null) {
            hook.run();
        }
        score = observed + points;
    }

    public int getScore() {
        return score;
    }

    public void reset() {
        score = 0;
    }
}
