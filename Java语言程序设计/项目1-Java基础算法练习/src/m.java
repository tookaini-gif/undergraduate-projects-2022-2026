import java.util.Scanner;
public class m {
    public static void main(String[] args) {
        try (Scanner in = new Scanner(System.in)) {
            long a = in.nextInt(), b = in.nextInt(), c = in.nextInt();
            long numerator = Math.max(a, Math.max(b, c));
            long left = Math.max(a + b, Math.max(b, c));
            long right = Math.max(a, Math.max(b, b + c));
            if (left == 0 || right == 0) throw new IllegalArgumentException("zero denominator");
            double result = numerator / ((double) left * right);
            System.out.printf(java.util.Locale.ROOT, "%.3f%n", result);
        }
    }
}
