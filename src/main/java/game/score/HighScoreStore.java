package game.score;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;

/**
 * Appends high-score lines to a text file.
 */
public class HighScoreStore {

    private final Path file;
    private volatile Runnable beforeWrite;

    public HighScoreStore(Path file) {
        if (file == null) {
            throw new IllegalArgumentException("file");
        }
        this.file = file;
    }

    public void setBeforeWrite(Runnable beforeWrite) {
        this.beforeWrite = beforeWrite;
    }

    public Path getFile() {
        return file;
    }

    public void save(String player, int points) throws IOException {
        if (player == null || player.isEmpty()) {
            throw new IllegalArgumentException("player");
        }
        if (points <= 0) {
            throw new IllegalArgumentException("points");
        }
        String line = player + ":" + points + "\n";
        Runnable hook = beforeWrite;
        if (hook != null) {
            hook.run();
        }
        // Defect: read-modify-write of the whole file without exclusion.
        List<String> existing = new ArrayList<String>();
        if (Files.exists(file)) {
            existing.addAll(Files.readAllLines(file, StandardCharsets.UTF_8));
        }
        existing.add(line.trim());
        StringBuilder body = new StringBuilder();
        for (int i = 0; i < existing.size(); i++) {
            body.append(existing.get(i)).append('\n');
        }
        Files.write(
                file,
                body.toString().getBytes(StandardCharsets.UTF_8),
                StandardOpenOption.CREATE,
                StandardOpenOption.TRUNCATE_EXISTING,
                StandardOpenOption.WRITE);
    }

    public List<String> readAll() throws IOException {
        if (!Files.exists(file)) {
            return new ArrayList<String>();
        }
        return Files.readAllLines(file, StandardCharsets.UTF_8);
    }
}
