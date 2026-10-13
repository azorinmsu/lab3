package game.world;

import java.util.ArrayList;
import java.util.List;

/**
 * Shared collection of snakes or other board objects.
 */
public class EntityRegistry {

    private final List<Entity> entities = new ArrayList<Entity>();
    private volatile Runnable beforeMutate;
    private volatile Runnable beforeIterate;

    public void setBeforeMutate(Runnable beforeMutate) {
        this.beforeMutate = beforeMutate;
    }

    public void setBeforeIterate(Runnable beforeIterate) {
        this.beforeIterate = beforeIterate;
    }

    public void add(Entity entity) {
        if (entity == null) {
            throw new IllegalArgumentException("entity");
        }
        Runnable hook = beforeMutate;
        if (hook != null) {
            hook.run();
        }
        entities.add(entity);
    }

    public void remove(Entity entity) {
        Runnable hook = beforeMutate;
        if (hook != null) {
            hook.run();
        }
        entities.remove(entity);
    }

    /**
     * Live view used by readers. The defective version exposes the raw list.
     */
    public List<Entity> view() {
        Runnable hook = beforeIterate;
        if (hook != null) {
            hook.run();
        }
        return entities;
    }

    /**
     * Snapshot of identifiers currently registered.
     */
    public List<String> snapshotIds() {
        List<String> ids = new ArrayList<String>();
        for (Entity entity : view()) {
            ids.add(entity.getId());
        }
        return ids;
    }

    public int size() {
        return entities.size();
    }
}
