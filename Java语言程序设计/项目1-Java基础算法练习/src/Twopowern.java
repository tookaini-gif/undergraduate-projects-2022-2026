import java.math.BigInteger;
import java.util.Scanner;
public class Twopowern {
    public static void main(String[] args) {
        try (Scanner in = new Scanner(System.in)) {
            int n = in.nextInt();
            if (n < 0) throw new IllegalArgumentException("n must be non-negative");
            System.out.println(BigInteger.ONE.shiftLeft(n));
        }
    }
}
