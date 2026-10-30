import java.util.Scanner;
public class Score {
    public static void main(String[] args) {
        try (Scanner in = new Scanner(System.in)) {
            int n = in.nextInt();
            if (n <= 0) throw new IllegalArgumentException("n must be positive");
            int best = Integer.MIN_VALUE;
            String name = "";
            for (int i = 0; i < n; i++) {
                int score = in.nextInt();
                String current = in.next();
                if (i == 0 || score > best) { best = score; name = current; }
            }
            System.out.println(name);
        }
    }
}
