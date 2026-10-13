package game.control;

public enum Direction {
    UP,
    DOWN,
    LEFT,
    RIGHT;

    public boolean isOpposite(Direction other) {
        if (other == null) {
            return false;
        }
        switch (this) {
            case UP:
                return other == DOWN;
            case DOWN:
                return other == UP;
            case LEFT:
                return other == RIGHT;
            case RIGHT:
                return other == LEFT;
            default:
                return false;
        }
    }
}
