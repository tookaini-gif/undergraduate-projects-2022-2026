import java.util.Scanner;
public class Delete {
    public static String stripSuffix(String word) {
        for (String suffix : new String[]{"ing", "er", "ly"}) {
            if (word.length() > suffix.length() && word.endsWith(suffix))
                return word.substring(0, word.length() - suffix.length());
        }
        return word;
    }
    public static void main(String[] args) {
        try (Scanner in = new Scanner(System.in)) {
            if (in.hasNext()) System.out.println(stripSuffix(in.next()));
        }
    }
}
