package game.collision;

/**
 * Processes a snake death / collision event at most once.
 */
public class CollisionProcessor {

    private boolean dead;
    private int deathEvents;
    private int scoreAwarded;
    private volatile Runnable beforeMarkDead;

    public void setBeforeMarkDead(Runnable beforeMarkDead) {
        this.beforeMarkDead = beforeMarkDead;
    }

    public boolean isDead() {
        return dead;
    }

    public int getDeathEvents() {
        return deathEvents;
    }

    public int getScoreAwarded() {
        return scoreAwarded;
    }

    /**
     * Handles a collision. Must award the death result at most once.
     */
    public void handleCollision(int bonus) {
        if (bonus < 0) {
            throw new IllegalArgumentException("bonus");
        }
        boolean alreadyDead = dead;
        Runnable hook = beforeMarkDead;
        if (hook != null) {
            hook.run();
        }
        if (alreadyDead) {
            return;
        }
        dead = true;
        deathEvents++;
        scoreAwarded += bonus;
    }
}
