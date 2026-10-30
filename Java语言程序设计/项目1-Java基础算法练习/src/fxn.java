import java.util.Scanner;
public class fxn
{
    public static void main(String[] args)
    {
        Scanner scanner = new Scanner(System.in);
        int x = scanner.nextInt();
        int n = scanner.nextInt();
        double ans=x;

        for(int i=1;i<=n;i++)
        {
            ans=x/(i+ans);
        }
        System.out.printf("%.2f\n",ans);
    }
}