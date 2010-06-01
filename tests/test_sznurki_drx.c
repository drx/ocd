#include <stdio.h>

int sznurki[1000010];
int main()
{
    int d, n_d, m, i, out = 0;
    scanf("%d", &m);
    for (i=0;i<m;i++)
    {
        scanf("%d %d", &d, &n_d);
        sznurki[d] = n_d;
    }
    for (i=0;i<1000001;i++)
    {
        int n = sznurki[i];
        if (i>500000)
        {
            for (; n; out++)
                n &= n - 1;
        }
        else
        {
            if (n > 1)
            {
                sznurki[2*i] += n/2;
            }
            if (n%2 == 1) out++; 
        }
    }
    printf("%d\n", out);
}
