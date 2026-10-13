package game.control;

/**
 * Accepts movement commands for one snake.
 * Within one tick, the applied direction must not become the opposite of the
 * direction recorded at {@link #beginTick()}.
 */
public class DirectionController {

    private Direction current = Direction.RIGHT;
    private Direction tickStart = Direction.RIGHT;
    private volatile Runnable beforeApply;

    public void setBeforeApply(Runnable beforeApply) {
        this.beforeApply = beforeApply;
    }

    public Direction getDirection() {
        return current;
    }

    public Direction getTickStart() {
        return tickStart;
    }

    /** Call once per game tick before accepting new input. */
    public void beginTick() {
        tickStart = current;
    }

    public void setDirection(Direction next) {
        if (next == null) {
            throw new IllegalArgumentException("direction");
        }
        Runnable hook = beforeApply;
        if (hook != null) {
            hook.run();
        }
        // Defect: validates against the live current direction, not tickStart,
        // and does so without excluding concurrent writers.
        if (current.isOpposite(next)) {
            return;
        }
        current = next;
    }
}
