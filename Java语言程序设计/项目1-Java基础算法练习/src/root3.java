import java.math.BigInteger;
import java.util.Scanner;
public class root3 {
    // Integer cube root truncated toward zero, without floating-point rounding.
    public static BigInteger cubeRoot(BigInteger n) {
        BigInteger value = n.abs(), low = BigInteger.ZERO;
        BigInteger high = BigInteger.ONE.shiftLeft((value.bitLength() + 2) / 3 + 1);
        while (high.subtract(low).compareTo(BigInteger.ONE) > 0) {
            BigInteger mid = low.add(high).shiftRight(1);
            if (mid.pow(3).compareTo(value) <= 0) low = mid;
            else high = mid;
        }
        return n.signum() < 0 ? low.negate() : low;
    }
    public static void main(String[] args) {
        try (Scanner in = new Scanner(System.in)) {
            System.out.println(cubeRoot(in.nextBigInteger()));
        }
    }
}
