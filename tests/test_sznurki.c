#include <stdlib.h>
#include <stdio.h>
#define SIZE 1000001
#define SIZE05 500001
int a[ SIZE ];
int sum, n, i, count, length, changed, c;
int main()
{
	scanf( "%d", &n );
	for( i = 0; i < n; ++i )
	{
		scanf("%d %d", &length, &count);
		a[ length ] = count;
	}	
	
	for( i = 1; i < SIZE05 ; ++i )
		if( a[ i ] )
		{
			sum += a[ i ] % 2;
			a[ 2*i ] += a[ i ] / 2;
		}
	
	for( i = SIZE05 ; i < SIZE; ++i )
	{
		if( a[ i ] )
		{
			for (c = 0; a[ i ]; c++)
			{
				a[ i ] &= a[ i ] - 1;
				sum++;
			}
		}
	}
	printf( "%d\n", sum );
}
