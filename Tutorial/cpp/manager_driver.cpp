#include "cpptypes.h"
#include "manager.h"
#include <stdio.h>

int main()
{
  OrderType order;
  Manager manager;
  int Total;

  char line[10];

#if defined (ORDER)
  line[0] = 'P';
#elif defined (CHECK)
  line[0] = 'G';
#else
  printf("P=PlaceOrder C=ClearTable G=GetCheckTotal A=AddIncludedDessert : ");
  scanf("%s",line);
#endif

  switch (line[0])
  {
    case 'p': case 'P':
      order.Entree = Steak;
      manager.PlaceOrder(1, 1, order);
      break;
    case 'g': case 'G':
      order.Entree = Chicken;
      manager.PlaceOrder(2, 2, order);
      Total = manager.GetCheckTotal(2);
      printf("The Total is %d\n", Total);
      break;
    case 'c': case 'C':
      manager.ClearTable(1);
      break;
    case 'a': case 'A':
      order.Entree = Steak;
      order.Salad = Caesar;
      order.Beverage = MixedDrink;
      manager.AddIncludedDessert(&order);
      break;
  }

  return 0;
}
