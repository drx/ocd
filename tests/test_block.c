int main()
{
	int sum=0;
	int x = 4;
	{
		sum+=x;
		int x = 3;
		{ 
			sum+=x;
			int x = 2;
			sum+=x;
		}
	}
	sum+=x;
}
