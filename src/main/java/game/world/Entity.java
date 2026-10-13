package game.world;

public final class Entity {

    private final String id;

    public Entity(String id) {
        if (id == null || id.isEmpty()) {
            throw new IllegalArgumentException("id");
        }
        this.id = id;
    }

    public String getId() {
        return id;
    }

    @Override
    public String toString() {
        return id;
    }
}
