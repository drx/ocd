int main()
{
    int a = 0;
    for (int i=0; i<1000; i++)
    {
        if (a > 500)
        {
            a += i;
        }
    }
}
