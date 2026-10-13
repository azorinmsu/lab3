package game;

import java.awt.Color;

import javax.swing.JFrame;

public class Main {
    public static void main(String[] args) {
        JFrame object = new JFrame();
        Gameplay gameplay = new Gameplay();
        object.setBounds(10, 10, 905, 700);
        object.setBackground(new Color(74, 153, 149));
        object.setResizable(false);
        object.setLocationRelativeTo(null);
        object.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        object.add(gameplay);
        gameplay.requestFocusInWindow();
        object.setVisible(true);
    }

}
