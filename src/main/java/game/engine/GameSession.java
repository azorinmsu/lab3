package game.engine;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Game tick state together with the high-score list.
 * Optional hooks let tests align the two call paths.
 * They do not change the recorded result.
 */
public class GameSession {

    private final Object engineLock = new Object();
    private final Object scoreLock = new Object();

    private int ticks;
    private int score;
    private final List<String> records = new ArrayList<String>();

    private volatile Runnable afterEngineLockAcquired;
    private volatile Runnable afterScoreLockAcquired;

    public void setAfterEngineLockAcquired(Runnable afterEngineLockAcquired) {
        this.afterEngineLockAcquired = afterEngineLockAcquired;
    }

    public void setAfterScoreLockAcquired(Runnable afterScoreLockAcquired) {
        this.afterScoreLockAcquired = afterScoreLockAcquired;
    }

    /**
     * Advance the session and append a high-score row for {@code player}.
     */
    public void updateAndRecord(String player, int points) {
        if (player == null || player.isEmpty()) {
            throw new IllegalArgumentException("player");
        }
        if (points <= 0) {
            throw new IllegalArgumentException("points");
        }
        synchronized (engineLock) {
            ticks++;
            score += points;
            Runnable hook = afterEngineLockAcquired;
            if (hook != null) {
                hook.run();
            }
            synchronized (scoreLock) {
                records.add(player + ":" + score);
            }
        }
    }

    /**
     * Read the high-score list and the current engine counters as one snapshot.
     */
    public String readRecordsAndState() {
        synchronized (scoreLock) {
            String listed = joinRecords();
            Runnable hook = afterScoreLockAcquired;
            if (hook != null) {
                hook.run();
            }
            synchronized (engineLock) {
                return listed + "|ticks=" + ticks + ",score=" + score;
            }
        }
    }

    public int getTicks() {
        synchronized (engineLock) {
            return ticks;
        }
    }

    public int getScore() {
        synchronized (engineLock) {
            return score;
        }
    }

    public List<String> getRecords() {
        synchronized (scoreLock) {
            return Collections.unmodifiableList(new ArrayList<String>(records));
        }
    }

    private String joinRecords() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < records.size(); i++) {
            if (i > 0) {
                sb.append(',');
            }
            sb.append(records.get(i));
        }
        return sb.toString();
    }
}
