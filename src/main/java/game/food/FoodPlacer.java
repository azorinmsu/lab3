package game.food;

import java.util.HashSet;
import java.util.Set;

/**
 * Places food on free board cells.
 */
public class FoodPlacer {

    private final Set<Long> occupied = new HashSet<Long>();
    private volatile Runnable betweenCheckAndPlace;

    public void setBetweenCheckAndPlace(Runnable betweenCheckAndPlace) {
        this.betweenCheckAndPlace = betweenCheckAndPlace;
    }

    public boolean place(int x, int y) {
        long key = key(x, y);
        boolean free = !occupied.contains(key);
        Runnable hook = betweenCheckAndPlace;
        if (hook != null) {
            hook.run();
        }
        if (!free) {
            return false;
        }
        occupied.add(key);
        return true;
    }

    public boolean isOccupied(int x, int y) {
        return occupied.contains(key(x, y));
    }

    public int size() {
        return occupied.size();
    }

    private static long key(int x, int y) {
        return (((long) x) << 32) ^ (y & 0xffffffffL);
    }
}
