package game;

import java.awt.Color;
import java.awt.Event;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.Random;

import javax.imageio.ImageIO;
import javax.swing.JPanel;
import javax.swing.Timer;

import game.engine.GameSession;
import game.score.ScoreCounter;

public class Gameplay extends JPanel implements KeyListener, ActionListener {

    /** How many pixels per tile? */
    private final int TILE_PIXELS = 25;

    private final int MAP_WIDTH = 34;
    private final int MAP_HEIGHT = 23;

    private int[] snakeXLength = new int[MAP_WIDTH * MAP_HEIGHT];
    private int[] snakeYLength = new int[MAP_WIDTH * MAP_HEIGHT];
    private int lengthOfSnake = 3;
    private int moves = 0;
    private final ScoreCounter scoreCounter = new ScoreCounter();
    private final GameSession gameSession = new GameSession();
    private boolean resultRecorded = false;

    private boolean left = false;
    private boolean right = true;
    private boolean up = false;
    private boolean down = false;

    private final BufferedImage gameScreen = new BufferedImage(MAP_WIDTH * TILE_PIXELS, MAP_HEIGHT * TILE_PIXELS,
                                                               BufferedImage.TYPE_INT_RGB);

    private final BufferedImage titleImage;
    private final BufferedImage snakeBody;
    private final BufferedImage foodIcon;
    private final BufferedImage rightMouth;
    private final BufferedImage upMouth;
    private final BufferedImage downMouth;
    private final BufferedImage leftMouth;

    private Timer timer;
    private int delay = 100;
    private Random random = new Random();

    private int xFood = random.nextInt(MAP_WIDTH);
    private int yFood = random.nextInt(MAP_HEIGHT);

    private boolean isGameOver = false;

    public Gameplay() {
        addKeyListener(this);
        setFocusable(true);

        timer = new Timer(delay, this);
        timer.start();

        // read all images
        try {
            titleImage = ImageIO.read(Gameplay.class.getResourceAsStream("/images/TitluSnake.png"));

            foodIcon = ImageIO.read(Gameplay.class.getResourceAsStream("/images/food.png"));

            snakeBody = ImageIO.read(Gameplay.class.getResourceAsStream("/images/snake/body.png"));

            rightMouth = ImageIO.read(Gameplay.class.getResourceAsStream("/images/snake/mouth/right.png"));
            upMouth = ImageIO.read(Gameplay.class.getResourceAsStream("/images/snake/mouth/up.png"));
            downMouth = ImageIO.read(Gameplay.class.getResourceAsStream("/images/snake/mouth/down.png"));
            leftMouth = ImageIO.read(Gameplay.class.getResourceAsStream("/images/snake/mouth/left.png"));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void paint(Graphics g) {
        if (moves == 0) {
            snakeXLength[2] = 1;
            snakeXLength[1] = 2;
            snakeXLength[0] = 3;

            snakeYLength[2] = 1;
            snakeYLength[1] = 1;
            snakeYLength[0] = 1;
        }

        // draw title image border
        g.setColor(Color.white);
        g.drawRect(24, 10, 851, 55);

        // draw title image
        g.drawImage(titleImage, 25, 11, null);

        // draw border for gameplay
        g.setColor(Color.white);
        g.drawRect(24, 74, 851, 577);

        // draw scores
        g.setColor(Color.white);
        g.setFont(new Font("Clibri", Font.PLAIN, 14));
        g.drawString("Scores:" + scoreCounter.getScore(), 780, 30);

        // draw length
        g.setColor(Color.white);
        g.setFont(new Font("Clibri", Font.PLAIN, 14));
        g.drawString("Length:" + lengthOfSnake, 780, 50);

        // gg -> game graphics
        Graphics gg = gameScreen.getGraphics();
        gg.setColor(Color.black);
        gg.clearRect(0, 0, gameScreen.getWidth(), gameScreen.getHeight());

        // --- DRAW TO GAME SCREEN --- \\
        for (int i = 0; i < lengthOfSnake; i++) {
            int x = snakeXLength[i];
            int y = snakeYLength[i];

            x *= TILE_PIXELS;
            y *= TILE_PIXELS;

            if (i == 0) {
                if (right) {
                    gg.drawImage(rightMouth, x, y, null);
                } else if (left) {
                    gg.drawImage(leftMouth, x, y, null);
                } else if (up) {
                    gg.drawImage(upMouth, x, y, null);
                } else if (down) {
                    gg.drawImage(downMouth, x, y, null);
                }
            } else {
                gg.drawImage(snakeBody, x, y, null);
            }

            if (xFood == snakeXLength[0] && yFood == snakeYLength[0]) {
                scoreCounter.addPoints(1);
                lengthOfSnake++;

                xFood = random.nextInt(MAP_WIDTH);
                yFood = random.nextInt(MAP_HEIGHT);

                snakeXLength[lengthOfSnake - 1] = snakeXLength[lengthOfSnake - 2];
                snakeYLength[lengthOfSnake - 1] = snakeYLength[lengthOfSnake - 2];
            }
            gg.drawImage(foodIcon, xFood * TILE_PIXELS, yFood * TILE_PIXELS, null);
        }

        // now that everything was drawn to game screen, draw the game screen to the panel
        gg.dispose();
        g.drawImage(gameScreen, 25, 75, null);

        for (int i = 1; i < lengthOfSnake; i++) {
            if (snakeXLength[i] == snakeXLength[0] && snakeYLength[i] == snakeYLength[0]) {
                left = false;
                up = false;
                right = false;
                down = false;

                isGameOver = true;
                recordResultOnce();

                g.setColor(Color.white);
                g.setFont(new Font("arial", Font.BOLD, 50));
                g.drawString("Game Over", 300, 300);

                g.setFont(new Font("arial", Font.BOLD, 20));
                g.drawString("Space to RESTART", 350, 340);
            }
        }
        g.dispose();
    }

    @Override
    public void keyPressed(KeyEvent e) {
        int code = e.getKeyCode();

        if (code == KeyEvent.VK_SPACE) {
            isGameOver = false;

            moves = 0;
            scoreCounter.reset();
            resultRecorded = false;
            lengthOfSnake = 3;

            up = false;
            left = false;
            down = false;
            right = true;

            repaint();
        } else if (code == KeyEvent.VK_RIGHT || code == KeyEvent.VK_D) {
            moves++;
            right = true;
            if (!left) {
                right = true;
            } else {
                right = false;
                left = true;
            }
            up = false;
            down = false;
        } else if (code == KeyEvent.VK_LEFT || code == KeyEvent.VK_A) {
            moves++;
            left = true;
            if (!right) {
                left = true;
            } else {
                right = true;
                left = false;
            }
            up = false;
            down = false;
        } else if (code == KeyEvent.VK_UP || code == KeyEvent.VK_W) {
            moves++;
            up = true;
            if (!down) {
                up = true;
            } else {
                down = true;
                up = false;
            }
            left = false;
            right = false;
        } else if (code == KeyEvent.VK_DOWN || code == KeyEvent.VK_S) {
            moves++;
            down = true;
            if (!up) {
                down = true;
            } else {
                down = false;
                up = true;
            }
            left = false;
            right = false;
        }
    }

    @Override
    public void keyReleased(KeyEvent e) {
    }

    @Override
    public void keyTyped(KeyEvent e) {
    }

    @Override
    public boolean keyDown(Event evt, int key) {
        return super.keyDown(evt, key);
    }

    @Override
    public boolean keyUp(Event evt, int key) {
        return super.keyUp(evt, key);
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        timer.start();

        if (isGameOver) return;

        if (right) {
            for (int i = lengthOfSnake - 1; i >= 0; i--) {
                if (i == 0) {
                    snakeXLength[i] += 1;
                } else {
                    snakeXLength[i] = snakeXLength[i - 1];
                    snakeYLength[i] = snakeYLength[i - 1];
                }
                if (snakeXLength[i] >= MAP_WIDTH) {
                    snakeXLength[i] = 0;
                }
            }
            repaint();
        } else if (left) {
            for (int i = lengthOfSnake - 1; i >= 0; i--) {
                if (i == 0) {
                    snakeXLength[i] -= 1;
                } else {
                    snakeXLength[i] = snakeXLength[i - 1];
                    snakeYLength[i] = snakeYLength[i - 1];
                }
                if (snakeXLength[i] < 0) {
                    snakeXLength[i] = MAP_WIDTH - 1;
                }
            }
            repaint();
        } else if (up) {
            for (int i = lengthOfSnake - 1; i >= 0; i--) {
                if (i == 0) {
                    snakeYLength[i] -= 1;
                } else {
                    snakeXLength[i] = snakeXLength[i - 1];
                    snakeYLength[i] = snakeYLength[i - 1];
                }
                if (snakeYLength[i] < 0) {
                    snakeYLength[i] = MAP_HEIGHT - 1;
                }
            }
            repaint();
        } else if (down) {
            for (int i = lengthOfSnake - 1; i >= 0; i--) {
                if (i == 0) {
                    snakeYLength[i] += 1;
                } else {
                    snakeXLength[i] = snakeXLength[i - 1];
                    snakeYLength[i] = snakeYLength[i - 1];
                }
                if (snakeYLength[i] >= MAP_HEIGHT) {
                    snakeYLength[i] = 0;
                }
            }
            repaint();
        }
    }

    /** Persist the final score once. Single-threaded UI path. */
    private void recordResultOnce() {
        if (resultRecorded) {
            return;
        }
        int points = scoreCounter.getScore();
        if (points <= 0) {
            return;
        }
        gameSession.updateAndRecord("Player", points);
        resultRecorded = true;
    }

}
