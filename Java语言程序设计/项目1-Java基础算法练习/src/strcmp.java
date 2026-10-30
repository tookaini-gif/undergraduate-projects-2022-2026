import java.util.Scanner;
public class strcmp
{
    public static void main(String[] args)
    {
        Scanner scanner = new Scanner(System.in);
        String content1= scanner.next();
        String content2= scanner.next();
        char[] str1=content1.toCharArray();
        char[] str2=content2.toCharArray();
        int len1 = str1.length;
        int len2 = str2.length;
        boolean ans=true;

        if(len1<len2)
        {
            ans= false;
        }

        else
        {
            for(int i=0;i<len2;i++)
            {
                if(str1[len1-len2+i]!=str2[i])
                {
                    ans=false;
                    break;
                }
            }
        }
        System.out.println(ans);
    } 
}